"""
配置管理插件 - 仅超级管理员可用
用于动态调整功能开关和权限设置
"""

import re
from datetime import datetime
from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, MessageEvent, Message
from nonebot.params import CommandArg

from services.permission import get_permission_level, PermissionLevel, check_command_permission, set_temp_permission, clear_temp_permission, get_all_temp_permissions, blacklist_store
import re
from services.message_utils import format_success, format_error, send_long_message
from services.group_config import group_config_store, COMMAND_DEFAULTS


# 配置管理命令 - 仅超级管理员可用
config_cmd = on_command("bot", priority=5, block=True)


@config_cmd.handle()
async def handle_config(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """配置管理主命令"""
    if isinstance(event, PrivateMessageEvent):
        await config_cmd.finish(format_error("此命令仅群聊可用"))
    # 检查是否为超级管理员
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await config_cmd.finish(format_error("此命令仅超级管理员可用"))
    
    text = args.extract_plain_text().strip()
    parts = text.split()
    
    if not parts:
        # 显示帮助信息
        help_msg = (
            "🔧 Bot 配置管理（仅超级管理员）\n"
            + "=" * 30 + "\n"
            "用法:\n"
            "#bot status - 查看当前群配置状态\n"
            "#bot list - 列出所有可配置命令\n"
            "#bot enable <命令> - 启用命令\n"
            "#bot disable <命令> - 禁用命令\n"
            "#bot permission <命令> <权限> - 设置权限\n"
            "#bot settemppermission @QQ <权限> - 临时设定某人权限 (重启失效)\n"
            "#bot cleartemppermission @QQ - 清除某人临时权限\n"
            "#bot temppermissions - 查看所有临时权限设置\n"
            "#bot blacklist add/remove/list/info - 黑名单管理 (需要 Lv3+ 权限)\n"
            "#bot reset [命令] - 重置配置\n\n"
            "权限等级:\n"
            "  -1/banned      - 被封禁用户\n"
            "  0/unbound_user - 未绑定成员\n"
            "  1/bound_user   - 已绑定成员\n"
            "  2/unbound_admin - 未绑定管理员\n"
            "  3/bound_admin  - 已绑定管理员\n"
            "  4/owner        - 群主\n"
            "  5/superuser    - 超级管理员"
        )
        await config_cmd.finish(help_msg)
    
    subcmd = parts[0].lower()
    
    if subcmd == "status":
        await handle_status(bot, event)
    elif subcmd == "list":
        await handle_list(bot, event)
    elif subcmd == "enable":
        if len(parts) < 2:
            await config_cmd.finish(format_error("请指定要启用的命令", "用法: #bot enable <命令>"))
        await handle_enable(bot, event, parts[1])
    elif subcmd == "disable":
        if len(parts) < 2:
            await config_cmd.finish(format_error("请指定要禁用的命令", "用法: #bot disable <命令>"))
        await handle_disable(bot, event, parts[1])
    elif subcmd == "permission":
        if len(parts) < 3:
            await config_cmd.finish(format_error(
                "参数不足",
                "用法: #bot permission <命令> <权限等级>\n权限: 0/unbound_user, 1/bound_user, 2/unbound_admin, 3/bound_admin, 4/owner, 5/superuser"
            ))
        await handle_permission(bot, event, parts[1], parts[2])
    elif subcmd == "reset":
        cmd_name = parts[1] if len(parts) > 1 else None
        await handle_reset(bot, event, cmd_name)
    elif subcmd == "settemppermission":
        if len(parts) < 2:
            await config_cmd.finish(format_error(
                "参数不足",
                "用法: #bot settemppermission @QQ <权限等级>"
            ))
        await handle_set_temp_permission(bot, event, parts[1])
    elif subcmd == "cleartemppermission":
        await handle_clear_temp_permission(bot, event)
    elif subcmd == "temppermissions":
        await handle_show_temp_permissions(bot, event)
    elif subcmd == "blacklist":
        # 硬限制：黑名单命令最低需要 Lv3 (BOUND_ADMIN)
        operator_level = await get_permission_level(bot, event)
        if operator_level < PermissionLevel.BOUND_ADMIN:
            await config_cmd.finish(format_error("❌ 权限不足：黑名单管理需要 Lv3 (已绑定管理员) 或更高权限"))
        
        if len(parts) < 2:
            await config_cmd.finish(format_error(
                "参数不足",
                "用法: #bot blacklist add/remove/list/info"
            ))
        await handle_blacklist(bot, event, parts[1:])
    else:
        await config_cmd.finish(format_error(f"未知子命令: {subcmd}", "使用 #bot 查看帮助"))


async def handle_status(bot: Bot, event: GroupMessageEvent):
    """查看当前群的配置状态"""
    config = group_config_store.get(str(event.group_id))
    
    msg = f"📊 当前群配置状态\n"
    msg += "=" * 30 + "\n"
    msg += f"默认VRChat群组: {config.default_vrc_group or '未设置'}\n"
    msg += f"通知功能: {'✅ 启用' if config.notify_enabled else '❌ 禁用'}\n"
    msg += f"管理操作: {'✅ 启用' if config.admin_ops_enabled else '❌ 禁用'}\n"
    msg += f"用户绑定: {'✅ 启用' if config.allow_user_bind else '❌ 禁用'}\n\n"
    
    # 统计已修改的命令配置
    modified_cmds = []
    for cmd_name, cmd_config in config.commands.items():
        defaults = COMMAND_DEFAULTS.get(cmd_name, {})
        if (cmd_config.enabled != defaults.get("enabled", True) or 
            cmd_config.permission != defaults.get("permission", PermissionLevel.UNBOUND_USER).value):
            modified_cmds.append((cmd_name, cmd_config))
    
    if modified_cmds:
        msg += f"已自定义的命令 ({len(modified_cmds)}个):\n"
        msg += "=" * 30 + "\n"
        for cmd_name, cmd_config in sorted(modified_cmds)[:20]:
            status = "✅" if cmd_config.enabled else "❌"
            perm_names = {
                -1: "被封禁用户", 0: "未绑定成员", 1: "已绑定成员", 
                2: "未绑定管理", 3: "已绑定管理", 
                4: "群主", 5: "超管"
            }
            perm = perm_names.get(cmd_config.permission, "?")
            
            # 显示友好的命令名称
            display_name = {
                "bot_blacklist": "blacklist (#bot blacklist)"
            }.get(cmd_name, cmd_name)
            
            msg += f"  {status} #{display_name} (权限: {perm})\n"
        
        if len(modified_cmds) > 20:
            msg += f"  ... 还有 {len(modified_cmds) - 20} 个"
    else:
        msg += "✨ 所有命令均使用默认配置"
    
    await config_cmd.finish(msg)


async def handle_list(bot: Bot, event: GroupMessageEvent):
    """列出所有可配置的命令"""
    config = group_config_store.get(str(event.group_id))
    
    msg = "📋 所有可配置命令\n"
    msg += "=" * 30 + "\n\n"
    
    # 按模块分组
    modules = {
        "系统/认证": ["vrclLogin", "2fa", "vrcCheck"],
        "查询": ["whereis", "instances", "whois"],
        "用户绑定": ["bind", "confirm", "unbind", "bindinfo"],
        "群组管理": ["gmembers", "ginvite", "gkick", "gban", "gunban", 
                   "grole", "grequests", "gaccept", "greject", 
                   "gannounce", "gdelannounce", "gaudit"],
        "Bot配置": ["bot_blacklist"],
    }
    
    for module_name, cmd_list in modules.items():
        msg += f"【{module_name}】\n"
        for cmd_name in cmd_list:
            cmd_config = config.commands.get(cmd_name)
            if cmd_config:
                status = "✅" if cmd_config.enabled else "❌"
                perm_names = {
                    -1: "被封禁用户", 0: "未绑定成员", 1: "已绑定成员", 
                    2: "未绑定管理", 3: "已绑定管理", 
                    4: "群主", 5: "超管"
                }
                perm = perm_names.get(cmd_config.permission, "?")
                
                # 标记与默认不同的配置
                defaults = COMMAND_DEFAULTS.get(cmd_name, {})
                is_default = (
                    cmd_config.enabled == defaults.get("enabled", True) and
                    cmd_config.permission == defaults.get("permission", PermissionLevel.UNBOUND_USER).value
                )
                marker = "" if is_default else " ⚙️"
                
                # 显示友好的命令名称
                display_name = {
                    "bot_blacklist": "blacklist (#bot blacklist)"
                }.get(cmd_name, cmd_name)
                
                msg += f"  {status} #{display_name} (权限: {perm}){marker}\n"
        msg += "\n"
    
    msg += "💡 标记 ⚙️ 表示已自定义配置"
    
    await send_long_message(config_cmd, msg)


async def handle_enable(bot: Bot, event: GroupMessageEvent, cmd_name: str):
    """启用指定命令"""
    if cmd_name not in COMMAND_DEFAULTS:
        await config_cmd.finish(format_error(
            f"未知命令: {cmd_name}",
            "使用 #bot list 查看所有可用命令"
        ))
    
    config = group_config_store.get(str(event.group_id))
    config.set_command_enabled(cmd_name, True)
    group_config_store.set(config)
    
    await config_cmd.finish(format_success(f"已启用命令 #{cmd_name}"))


async def handle_disable(bot: Bot, event: GroupMessageEvent, cmd_name: str):
    """禁用指定命令"""
    if cmd_name not in COMMAND_DEFAULTS:
        await config_cmd.finish(format_error(
            f"未知命令: {cmd_name}",
            "使用 #bot list 查看所有可用命令"
        ))
    
    # 不允许禁用 bot 命令本身
    if cmd_name == "bot":
        await config_cmd.finish(format_error("不能禁用配置管理命令"))
    
    config = group_config_store.get(str(event.group_id))
    config.set_command_enabled(cmd_name, False)
    group_config_store.set(config)
    
    await config_cmd.finish(format_success(f"已禁用命令 #{cmd_name}"))


async def handle_permission(bot: Bot, event: GroupMessageEvent, cmd_name: str, perm_str: str):
    """设置命令权限"""
    if cmd_name not in COMMAND_DEFAULTS:
        await config_cmd.finish(format_error(
            f"未知命令: {cmd_name}",
            "使用 #bot list 查看所有可用命令"
        ))
    
    # 解析权限等级
    try:
        perm_level = PermissionLevel.from_str(perm_str)
    except KeyError:
        await config_cmd.finish(format_error(
            f"无效的权限等级: {perm_str}",
            "有效值: -1/banned, 0/unbound_user, 1/bound_user, 2/unbound_admin, 3/bound_admin, 4/owner, 5/superuser"
        ))
    
    # 不允许降低 bot 命令的权限
    if cmd_name == "bot" and perm_level < PermissionLevel.SUPERUSER:
        await config_cmd.finish(format_error("配置管理命令必须保持超级管理员权限"))
    
    config = group_config_store.get(str(event.group_id))
    config.set_command_permission(cmd_name, perm_level)
    group_config_store.set(config)
    
    perm_names = {
        -1: "被封禁用户", 0: "未绑定成员", 1: "已绑定成员", 
        2: "未绑定管理员", 3: "已绑定管理员", 
        4: "群主", 5: "超级管理员"
    }
    await config_cmd.finish(
        format_success(f"已设置 #{cmd_name} 的权限为: {perm_names.get(perm_level.value, '未知')}")
    )


async def handle_reset(bot: Bot, event: GroupMessageEvent, cmd_name: str = None):
    """重置配置"""
    config = group_config_store.get(str(event.group_id))
    
    if cmd_name:
        # 重置单个命令
        if cmd_name not in COMMAND_DEFAULTS:
            await config_cmd.finish(format_error(
                f"未知命令: {cmd_name}",
                "使用 #bot list 查看所有可用命令"
            ))
        
        defaults = COMMAND_DEFAULTS[cmd_name]
        config.set_command_enabled(cmd_name, defaults["enabled"])
        config.set_command_permission(cmd_name, defaults["permission"])
        group_config_store.set(config)
        
        await config_cmd.finish(format_success(f"已重置 #{cmd_name} 的配置为默认值"))
    else:
        # 重置所有命令配置
        config.commands.clear()
        config.model_post_init(None)
        group_config_store.set(config)
        
        await config_cmd.finish(format_success("已重置所有命令配置为默认值"))


def _extract_at_qq(event: GroupMessageEvent) -> str | None:
    """从消息中提取第一个 @QQ 号"""
    # 1. 尝试从事件原始消息解析 CQ 码 [CQ:at,qq=xxx] 或 NapCat 格式 [at:qq=xxx]
    raw = getattr(event, 'raw_message', '') or str(event.get_message())
    m = re.search(r'\[CQ:at,qq=(\d+)\]', raw)
    if not m:
        m = re.search(r'\[at:qq=(\d+)\]', raw)
    if m:
        return m.group(1)
    # 2. 段遍历回退
    for seg in event.get_message():
        if seg.type == "at":
            qq = seg.data.get("qq", "")
            if qq and qq != "all":
                return str(qq)
    return None


async def handle_set_temp_permission(bot: Bot, event: GroupMessageEvent, perm_str: str):
    """设置临时权限"""
    at_qq = _extract_at_qq(event)
    
    if not at_qq:
        await config_cmd.finish(format_error("请 @ 要设置权限的用户"))
    
    # 解析权限等级
    try:
        perm_level = PermissionLevel.from_str(perm_str)
    except KeyError:
        await config_cmd.finish(format_error(
            f"无效的权限等级: {perm_str}",
            "有效值: -1/banned, 0/unbound_user, 1/bound_user, 2/unbound_admin, 3/bound_admin, 4/owner, 5/superuser"
        ))
    
    # 安全限制：不能通过此命令将自己或他人的权限提升到 SUPERUSER
    if perm_level >= PermissionLevel.SUPERUSER and at_qq not in bot.config.superusers:
        await config_cmd.finish(format_error("禁止通过此命令赋予超级管理员权限"))
    
    set_temp_permission(at_qq, perm_level)
    
    perm_names = {
        -1: "被封禁用户", 0: "未绑定成员", 1: "已绑定成员", 
        2: "未绑定管理", 3: "已绑定管理", 
        4: "群主", 5: "超管"
    }
    await config_cmd.finish(
        format_success(f"已临时设置 QQ {at_qq} 的权限为: {perm_names.get(perm_level.value, '未知')} (重启后失效)")
    )


async def handle_clear_temp_permission(bot: Bot, event: GroupMessageEvent):
    """清除临时权限"""
    at_qq = _extract_at_qq(event)
    
    if not at_qq:
        await config_cmd.finish(format_error("请 @ 要清除临时权限的用户"))
    
    clear_temp_permission(at_qq)
    await config_cmd.finish(format_success(f"已清除 QQ {at_qq} 的临时权限"))


async def handle_show_temp_permissions(bot: Bot, event: GroupMessageEvent):
    """显示所有临时权限设置"""
    temp_perms = get_all_temp_permissions()
    
    if not temp_perms:
        await config_cmd.finish("✨ 当前没有设置任何临时权限")
    
    msg = f"📋 临时权限列表 (共 {len(temp_perms)} 人)\n"
    msg += "=" * 30 + "\n"
    
    perm_names = {
        -1: "被封禁用户", 0: "未绑定成员", 1: "已绑定成员", 
        2: "未绑定管理", 3: "已绑定管理", 
        4: "群主", 5: "超管"
    }
    
    for qq_id, level in sorted(temp_perms.items()):
        level_name = perm_names.get(level.value, "未知")
        msg += f"• QQ: {qq_id}\n"
        msg += f"  临时权限: {level_name} (Lv{level.value})\n\n"
    
    msg += "💡 提示: 这些设置仅在本次运行期间有效，重启 Bot 后将自动清除。"
    
    await send_long_message(config_cmd, msg)


async def handle_blacklist(bot: Bot, event: GroupMessageEvent, args: list):
    """黑名单管理主函数"""
    # 注意：权限检查已在调用前完成（硬限制 Lv3+）
    
    # 检查配置系统：功能是否启用 + 软限制权限
    allowed, error_msg = await check_command_permission(bot, event, "bot_blacklist")
    if not allowed:
        await config_cmd.finish(error_msg)
    
    # 获取 operator_level 用于后续的层级验证
    operator_level = await get_permission_level(bot, event)
    
    action = args[0].lower() if args else ""
    
    if action == "add":
        await handle_blacklist_add(bot, event, operator_level, args[1:])
    elif action == "remove":
        await handle_blacklist_remove(bot, event, operator_level, args[1:])
    elif action == "list":
        await handle_blacklist_list(bot, event)
    elif action == "info":
        await handle_blacklist_info(bot, event, args[1:])
    else:
        await config_cmd.finish(format_error(
            f"未知操作: {action}",
            "用法: #bot blacklist add/remove/list/info"
        ))


async def handle_blacklist_add(bot: Bot, event: GroupMessageEvent, operator_level: PermissionLevel, args: list):
    """封禁用户"""
    if len(args) < 1:
        await config_cmd.finish(format_error(
            "参数不足",
            "用法: #bot blacklist add @某人 [原因]"
        ))
    
    # 提取被@的用户
    target_qq = _extract_at_qq(event)
    if not target_qq:
        await config_cmd.finish(format_error("请 @ 要封禁的用户"))
    
    # 提取封禁原因（剩余参数）
    reason = " ".join(args[1:]) if len(args) > 1 else "未说明"
    
    # 获取目标用户的权限等级
    # 构造一个模拟事件来获取目标用户的权限
    from nonebot.adapters.onebot.v11 import MessageSegment
    fake_event = event.copy()
    fake_event.user_id = int(target_qq)
    target_level = await get_permission_level(bot, fake_event)
    
    # 权限层级验证：高权限才能封禁低权限（除非互为超管）
    if operator_level != PermissionLevel.SUPERUSER or target_level != PermissionLevel.SUPERUSER:
        if target_level >= operator_level:
            await config_cmd.finish(format_error(
                f"❌ 权限不足：无法封禁权限等级高于或等于你的用户\n"
                f"你的权限: Lv{operator_level.value} ({operator_level.name})\n"
                f"目标权限: Lv{target_level.value} ({target_level.name})"
            ))
    
    # 检查是否已经在黑名单中
    if blacklist_store.is_blacklisted(target_qq):
        await config_cmd.finish(format_error(f"QQ {target_qq} 已在黑名单中"))
    
    # 执行封禁
    group_id = str(event.group_id)
    group_name = getattr(event.sender, 'card', None) or getattr(event.sender, 'nickname', '未知群')
    message_context = str(event.get_message())[:200]  # 截取前200字符作为上下文
    
    success = blacklist_store.add_ban(
        banned_qq=target_qq,
        banned_by=str(event.user_id),
        reason=reason,
        group_id=group_id,
        group_name=group_name,
        message_context=message_context,
        ban_type="manual"
    )
    
    if success:
        await config_cmd.finish(format_success(
            f"✅ 已将 QQ {target_qq} 加入黑名单\n"
            f"原因: {reason}\n"
            f"该用户将被禁止使用所有命令 (Lv-1)"
        ))
    else:
        await config_cmd.finish(format_error("封禁失败，请稍后重试"))


async def handle_blacklist_remove(bot: Bot, event: GroupMessageEvent, operator_level: PermissionLevel, args: list):
    """解封用户"""
    if len(args) < 1:
        await config_cmd.finish(format_error(
            "参数不足",
            "用法: #bot blacklist remove @某人 [原因]"
        ))
    
    # 提取被@的用户
    target_qq = _extract_at_qq(event)
    if not target_qq:
        await config_cmd.finish(format_error("请 @ 要解封的用户"))
    
    # 提取解封原因
    reason = " ".join(args[1:]) if len(args) > 1 else "未说明"
    
    # 检查是否在黑名单中
    if not blacklist_store.is_blacklisted(target_qq):
        await config_cmd.finish(format_error(f"QQ {target_qq} 不在黑名单中"))
    
    # 获取被封禁信息，检查封禁者权限
    ban_info = blacklist_store.get_ban_info(target_qq)
    if ban_info:
        banned_by = ban_info.get("banned_by", "")
        # 如果是超管封的，只有超管能解（或者被封者自己是超管）
        if banned_by in bot.config.superusers and str(event.user_id) not in bot.config.superusers:
            await config_cmd.finish(format_error("❌ 此封禁由超级管理员执行，仅超管可解除"))
    
    # 执行解封
    success = blacklist_store.remove_ban(
        qq_id=target_qq,
        removed_by=str(event.user_id),
        reason=reason
    )
    
    if success:
        await config_cmd.finish(format_success(
            f"✅ 已将 QQ {target_qq} 从黑名单移除\n"
            f"原因: {reason}\n"
            f"该用户已恢复正常权限"
        ))
    else:
        await config_cmd.finish(format_error("解封失败，请稍后重试"))


async def handle_blacklist_list(bot: Bot, event: GroupMessageEvent):
    """查看黑名单列表"""
    active_bans = blacklist_store.get_all_bans(active_only=True)
    
    if not active_bans:
        await config_cmd.finish("✨ 当前黑名单为空")
    
    msg = f"🚫 黑名单列表 (共 {len(active_bans)} 人)\n"
    msg += "=" * 40 + "\n\n"
    
    for i, ban_info in enumerate(active_bans[:20], 1):  # 最多显示20条
        banned_qq = ban_info.get("banned_qq", "未知")
        banned_by = ban_info.get("banned_by", "未知")
        reason = ban_info.get("reason", "未说明")
        banned_at = ban_info.get("banned_at", "未知")
        group_name = ban_info.get("group_name", "未知")
        
        # 格式化时间
        try:
            dt = datetime.fromisoformat(banned_at)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = banned_at
        
        msg += f"{i}. QQ: {banned_qq}\n"
        msg += f"   封禁者: {banned_by}\n"
        msg += f"   原因: {reason}\n"
        msg += f"   时间: {formatted_time}\n"
        msg += f"   地点: {group_name}\n"
        msg += "\n"
    
    if len(active_bans) > 20:
        msg += f"... 还有 {len(active_bans) - 20} 条记录\n\n"
    
    msg += "💡 使用 #bot blacklist info @某人 查看详细信息"
    
    await send_long_message(config_cmd, msg)


async def handle_blacklist_info(bot: Bot, event: GroupMessageEvent, args: list):
    """查看封禁详情"""
    if len(args) < 1:
        await config_cmd.finish(format_error(
            "参数不足",
            "用法: #bot blacklist info @某人"
        ))
    
    # 提取被@的用户
    target_qq = _extract_at_qq(event)
    if not target_qq:
        await config_cmd.finish(format_error("请 @ 要查询的用户"))
    
    ban_info = blacklist_store.get_ban_info(target_qq)
    
    if not ban_info:
        await config_cmd.finish(format_error(f"QQ {target_qq} 没有封禁记录"))
    
    status = ban_info.get("status", "unknown")
    status_text = {
        "active": "🚫 活跃（封禁中）",
        "removed": "✅ 已解除",
        "expired": "⏰ 已过期"
    }.get(status, f"❓ 未知状态 ({status})")
    
    msg = f"📋 封禁详细信息 - QQ {target_qq}\n"
    msg += "=" * 40 + "\n\n"
    msg += f"状态: {status_text}\n\n"
    
    # 封禁信息
    msg += "【封禁信息】\n"
    msg += f"封禁者: {ban_info.get('banned_by', '未知')}\n"
    msg += f"封禁时间: {ban_info.get('banned_at', '未知')}\n"
    msg += f"封禁原因: {ban_info.get('reason', '未说明')}\n"
    msg += f"封禁类型: {ban_info.get('ban_type', 'manual')}\n"
    msg += f"发生群组: {ban_info.get('group_name', '未知')} ({ban_info.get('group_id', 'N/A')})\n"
    
    if ban_info.get('message_context'):
        ctx = ban_info['message_context']
        if len(ctx) > 100:
            ctx = ctx[:100] + "..."
        msg += f"消息上下文: {ctx}\n"
    
    msg += "\n"
    
    # 解封信息（如果有）
    if status == "removed":
        msg += "【解封信息】\n"
        msg += f"解封者: {ban_info.get('removed_by', '未知')}\n"
        msg += f"解封时间: {ban_info.get('removed_at', '未知')}\n"
        msg += f"解封原因: {ban_info.get('remove_reason', '未说明')}\n"
    
    await config_cmd.finish(msg)
