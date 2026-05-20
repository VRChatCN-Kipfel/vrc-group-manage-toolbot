"""
群组绑定插件
提供 QQ 群与 VRChat 群组的绑定管理功能
"""

from nonebot import on_command, on_notice, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, Message, NoticeEvent, GroupIncreaseNoticeEvent
from nonebot.params import CommandArg
from nonebot.typing import T_State

from utils import get_vrc_client
from services.permission import get_permission_level, PermissionLevel, check_command_permission
from services.group_config import group_config_store
from services.message_utils import format_success, format_error, send_long_message
from services.global_config import global_config


# ── bindgroup ──

bindgroup_cmd = on_command("bindgroup", priority=5, block=True)


@bindgroup_cmd.handle()
async def handle_bindgroup(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, 
                           args: Message = CommandArg()):
    text = args.extract_plain_text().strip()
    logger.debug(f"bindgroup handler: event={type(event).__name__}, text={text!r}")
    
    # 情况1：无参数 - 查询当前绑定状态（任何人可用）
    if not text:
        await _handle_query(bot, event)
        return
    
    # 情况1b：私聊中纯数字 QQ 群号 → 查询该群绑定状态
    if isinstance(event, PrivateMessageEvent) and text.isdigit():
        level = await get_permission_level(bot, event)
        if level < PermissionLevel.SUPERUSER:
            await bindgroup_cmd.finish(format_error("私聊查询需要机器人超级管理员权限"))
        await _handle_query(bot, event, qq_group_id=text)
        return
    
    # 情况2：解绑操作（仅超管可用）
    if text.lower() in ("unbind", "--unbind", "-u"):
        level = await get_permission_level(bot, event)
        if level < PermissionLevel.SUPERUSER:
            await bindgroup_cmd.finish(format_error("解绑操作需要机器人超级管理员权限"))
        await _handle_unbind(bot, event)
        return
    
    # 情况2b：私聊解绑指定群 #bindgroup unbind <QQ群号>
    parts = text.split()
    if parts[0].lower() in ("unbind", "--unbind", "-u") and len(parts) > 1:
        level = await get_permission_level(bot, event)
        if level < PermissionLevel.SUPERUSER:
            await bindgroup_cmd.finish(format_error("解绑操作需要机器人超级管理员权限"))
        await _handle_unbind(bot, event, qq_group_id=parts[1])
        return
    
    # 情况3：绑定操作（仅超管可用）
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await bindgroup_cmd.finish(format_error("绑定/解绑操作需要机器人超级管理员权限"))
    
    await _handle_bind(bot, event, text)


async def _handle_query(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, qq_group_id: str = None):
    """处理查询请求"""
    
    if isinstance(event, GroupMessageEvent):
        # 群聊中查询
        qq_group_id = str(event.group_id)
    
    if not qq_group_id:
        await bindgroup_cmd.finish(format_error(
            "私聊查询需要指定 QQ 群号",
            "用法: #bindgroup <QQ群号>"
        ))
    
    config = group_config_store.get(qq_group_id)
    
    if not config.default_vrc_group:
        await bindgroup_cmd.finish(format_error(
            f"QQ 群 {qq_group_id} 尚未绑定 VRChat 群组",
            "请联系管理员使用 #bindgroup <grp_xxx> 进行绑定"
        ))
    
    vrc_group_id = config.default_vrc_group
    bound_qq_groups = group_config_store.get_by_vrc_group(vrc_group_id)
    
    # 尝试获取群组名称
    vrc_client = get_vrc_client()
    group_name = vrc_group_id
    if vrc_client.config.auth_cookie:
        try:
            group = await vrc_client.get_group(vrc_group_id)
            if group and group.name:
                group_name = f"{group.name} ({vrc_group_id})"
        except Exception:
            pass
    
    msg = f"🔗 群组绑定信息\n"
    msg += "=" * 24 + "\n"
    msg += f"VRChat 群组: {group_name}\n"
    msg += f"已绑定 QQ 群 ({len(bound_qq_groups)}个):\n"
    
    for qq_id in bound_qq_groups:
        is_group_chat = isinstance(event, GroupMessageEvent)
        marker = " ← 当前" if is_group_chat and qq_id == str(event.group_id) else ""
        msg += f"  • {qq_id}{marker}\n"
    
    await send_long_message(bindgroup_cmd, msg)


async def _handle_unbind(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, qq_group_id: str = None):
    """处理解绑操作"""
    
    if isinstance(event, GroupMessageEvent):
        qq_group_id = str(event.group_id)
    
    if not qq_group_id:
        await bindgroup_cmd.finish(format_error(
            "私聊解绑需要指定 QQ 群号",
            "用法: #bindgroup unbind <QQ群号>"
        ))
    
    config = group_config_store.get(qq_group_id)
    
    if not config.default_vrc_group:
        await bindgroup_cmd.finish(format_error(
            f"QQ 群 {qq_group_id} 尚未绑定任何 VRChat 群组",
            "无需解绑"
        ))
    
    vrc_group_id = config.default_vrc_group
    config.default_vrc_group = None
    group_config_store.set(config)
    
    await bindgroup_cmd.finish(format_success(
        f"已解除 QQ 群 {qq_group_id} 与 VRChat 群组 {vrc_group_id} 的绑定"
    ))


async def _handle_bind(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, text: str):
    """处理绑定/解绑操作"""
    
    parts = text.split()
    vrc_group_id = parts[0]
    
    # 验证 VRChat 群组 ID 格式
    if not vrc_group_id.startswith("grp_"):
        await bindgroup_cmd.finish(format_error(
            "VRChat 群组 ID 格式不正确",
            "应以 grp_ 开头，例如: grp_xxxxxxxx"
        ))
    
    if isinstance(event, GroupMessageEvent):
        # 群聊中绑定/解绑
        qq_group_id = str(event.group_id)
        
        # 检查是否已绑定到其他群组
        current_config = group_config_store.get(qq_group_id)
        if current_config.default_vrc_group and current_config.default_vrc_group != vrc_group_id:
            await bindgroup_cmd.finish(format_error(
                f"当前群聊已绑定到其他 VRChat 群组: {current_config.default_vrc_group}",
                "如需更换绑定，请先联系管理员解绑后再重新绑定"
            ))
        
        # 执行绑定或更新
        current_config.default_vrc_group = vrc_group_id
        group_config_store.set(current_config)
        
        await bindgroup_cmd.finish(format_success(
            f"已将当前群聊绑定到 VRChat 群组: {vrc_group_id}"
        ))
    
    else:
        # 私聊中绑定，需要提供 QQ 群号
        if len(parts) < 2:
            await bindgroup_cmd.finish(format_error(
                "私聊绑定需要指定 QQ 群号",
                "用法: #bindgroup <grp_xxx> <QQ群号>"
            ))
        
        qq_group_id = parts[1]
        
        # 验证 QQ 群号格式
        if not qq_group_id.isdigit():
            await bindgroup_cmd.finish(format_error(
                "QQ 群号格式不正确",
                "应为纯数字，例如: 123456789"
            ))
        
        # 检查该 QQ 群是否已绑定到其他群组
        current_config = group_config_store.get(qq_group_id)
        if current_config.default_vrc_group and current_config.default_vrc_group != vrc_group_id:
            await bindgroup_cmd.finish(format_error(
                f"QQ 群 {qq_group_id} 已绑定到其他 VRChat 群组: {current_config.default_vrc_group}",
                "如需更换绑定，请先解绑后再重新绑定"
            ))
        
        # 执行绑定
        current_config.default_vrc_group = vrc_group_id
        group_config_store.set(current_config)
        
        await bindgroup_cmd.finish(format_success(
            f"已将 QQ 群 {qq_group_id} 绑定到 VRChat 群组: {vrc_group_id}"
        ))


welcome_cmd = on_command("welcome", priority=5, block=True)

@welcome_cmd.handle()
async def handle_welcome(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 仅群聊可用
    if isinstance(event, PrivateMessageEvent):
        await welcome_cmd.finish(format_error("此命令仅群聊可用"))
    
    qq_group_id = str(event.group_id)
    text = args.extract_plain_text().strip()
    parts = text.split(maxsplit=1)
    subcmd = parts[0].lower() if parts else ""
    
    # 查询欢迎语：需要基础权限（默认 UNBOUND_USER，等级 0）
    # 这样可以拦截黑名单用户，但允许普通成员查看
    if not subcmd or subcmd == "status":
        allowed, error_msg = await check_command_permission(bot, event, "welcome")
        if not allowed:
            await welcome_cmd.finish(error_msg)
            
        config = group_config_store.get(qq_group_id)
        if not config.welcome_message:
            await welcome_cmd.finish("当前群未设置欢迎消息")
        
        msg = f"📢 当前欢迎消息:\n{'='*20}\n{config.welcome_message}"
        await send_long_message(welcome_cmd, msg)
        return

    allowed, error_msg = await check_command_permission(bot, event, "welcome_set")
    if not allowed:
        await welcome_cmd.finish(error_msg)

    if subcmd == "set":
        if len(parts) < 2:
            await welcome_cmd.finish(format_error(
                "请提供欢迎语内容",
                "用法: #welcome set <内容>\n支持变量: {at}, {name}, {vrc_name}"
            ))
        
        content = parts[1]
        config = group_config_store.get(qq_group_id)
        config.welcome_message = content
        group_config_store.set(config)
        
        await welcome_cmd.finish(format_success("欢迎消息已更新"))
    
    # 4. 清空欢迎语
    elif subcmd in ("clear", "delete", "remove"):
        config = group_config_store.get(qq_group_id)
        if not config.welcome_message:
            await welcome_cmd.finish("当前群未设置欢迎消息，无需清空")
        
        config.welcome_message = None
        group_config_store.set(config)
        
        await welcome_cmd.finish(format_success("欢迎消息已清空"))
    
    else:
        await welcome_cmd.finish(format_error(
            "未知子命令",
            "用法:\n#welcome - 查看当前设置\n#welcome set <内容> - 设置欢迎语\n#welcome clear - 清空欢迎语"
        ))


# ── 欢迎消息监听器 ──

@on_notice(priority=5, block=False)
async def handle_group_increase(bot: Bot, event: NoticeEvent):
    """监听群成员增加事件并发送欢迎消息"""
    if not isinstance(event, GroupIncreaseNoticeEvent):
        return

    if not global_config.is_welcome_enabled:
        return
    
    qq_group_id = str(event.group_id)
    user_id = str(event.user_id)

    config = group_config_store.get(qq_group_id)
    welcome_msg = config.welcome_message

    if not welcome_msg:
        return
    
    try:
        member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
        nickname = member_info.get("card") or member_info.get("nickname") or "新成员"

        from services.user_binding import user_binding_store
        binding = user_binding_store.get_by_qq(user_id)
        vrc_name = binding.vrc_display_name if binding else "未绑定"

        final_msg = welcome_msg.replace("{at}", f"[CQ:at,qq={user_id}]")
        final_msg = final_msg.replace("{name}", nickname)
        final_msg = final_msg.replace("{vrc_name}", vrc_name)

        await bot.send_group_msg(group_id=event.group_id, message=final_msg)
        logger.info(f"已向群 {qq_group_id} 的新成员 {user_id} 发送欢迎消息")
        
    except Exception as e:
        logger.error(f"发送欢迎消息失败: {e}")
