"""
群组绑定插件
提供 QQ 群与 VRChat 群组的绑定管理功能
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.typing import T_State

from utils import get_vrc_client
from services.permission import get_permission_level, PermissionLevel
from services.group_config import group_config_store
from services.message_utils import format_success, format_error, send_long_message


# ── bindgroup ──

bindgroup_cmd = on_command("bindgroup", priority=5, block=True)


@bindgroup_cmd.handle()
async def handle_bindgroup(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, 
                           args: Message = CommandArg()):
    text = args.extract_plain_text().strip()
    logger.debug(f"bindgroup 处理: 事件={type(event).__name__}, 文本={text!r}")
    
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
