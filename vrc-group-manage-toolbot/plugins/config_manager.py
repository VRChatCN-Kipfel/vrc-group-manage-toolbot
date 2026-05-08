"""
配置管理插件 - 仅超级管理员可用
用于动态调整功能开关和权限设置
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg

from services.permission import get_permission_level, PermissionLevel, check_command_permission
from services.message_utils import format_success, format_error, send_long_message
from services.group_config import group_config_store, COMMAND_DEFAULTS


# 配置管理命令 - 仅超级管理员可用
config_cmd = on_command("bot", priority=5, block=True)


@config_cmd.handle()
async def handle_config(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """配置管理主命令"""
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
            "─" * 30 + "\n"
            "用法:\n"
            "#bot status - 查看当前群配置状态\n"
            "#bot list - 列出所有可配置命令\n"
            "#bot enable <命令> - 启用命令\n"
            "#bot disable <命令> - 禁用命令\n"
            "#bot permission <命令> <权限> - 设置权限\n"
            "#bot reset [命令] - 重置配置\n\n"
            "权限等级:\n"
            "  0/user - 普通用户\n"
            "  1/admin - 群管理员\n"
            "  2/superuser - 超级管理员"
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
                "用法: #bot permission <命令> <权限等级>\n权限: 0/user, 1/admin, 2/superuser"
            ))
        await handle_permission(bot, event, parts[1], parts[2])
    elif subcmd == "reset":
        cmd_name = parts[1] if len(parts) > 1 else None
        await handle_reset(bot, event, cmd_name)
    else:
        await config_cmd.finish(format_error(f"未知子命令: {subcmd}", "使用 #bot 查看帮助"))


async def handle_status(bot: Bot, event: GroupMessageEvent):
    """查看当前群的配置状态"""
    config = group_config_store.get(str(event.group_id))
    
    msg = f"📊 当前群配置状态\n"
    msg += "─" * 30 + "\n"
    msg += f"默认VRChat群组: {config.default_vrc_group or '未设置'}\n"
    msg += f"通知功能: {'✅ 启用' if config.notify_enabled else '❌ 禁用'}\n"
    msg += f"管理操作: {'✅ 启用' if config.admin_ops_enabled else '❌ 禁用'}\n"
    msg += f"用户绑定: {'✅ 启用' if config.allow_user_bind else '❌ 禁用'}\n\n"
    
    # 统计已修改的命令配置
    modified_cmds = []
    for cmd_name, cmd_config in config.commands.items():
        defaults = COMMAND_DEFAULTS.get(cmd_name, {})
        if (cmd_config.enabled != defaults.get("enabled", True) or 
            cmd_config.permission != defaults.get("permission", PermissionLevel.USER).value):
            modified_cmds.append((cmd_name, cmd_config))
    
    if modified_cmds:
        msg += f"已自定义的命令 ({len(modified_cmds)}个):\n"
        msg += "─" * 30 + "\n"
        for cmd_name, cmd_config in sorted(modified_cmds)[:20]:
            status = "✅" if cmd_config.enabled else "❌"
            perm_names = {0: "用户", 1: "管理", 2: "超管"}
            perm = perm_names.get(cmd_config.permission, "?")
            msg += f"  {status} #{cmd_name} (权限: {perm})\n"
        
        if len(modified_cmds) > 20:
            msg += f"  ... 还有 {len(modified_cmds) - 20} 个"
    else:
        msg += "✨ 所有命令均使用默认配置"
    
    await config_cmd.finish(msg)


async def handle_list(bot: Bot, event: GroupMessageEvent):
    """列出所有可配置的命令"""
    config = group_config_store.get(str(event.group_id))
    
    msg = "📋 所有可配置命令\n"
    msg += "─" * 30 + "\n\n"
    
    # 按模块分组
    modules = {
        "系统/认证": ["vrclLogin", "2fa", "vrcCheck"],
        "查询": ["whereis", "instances", "whois"],
        "用户绑定": ["bind", "confirm", "unbind", "bindinfo"],
        "群组管理": ["gmembers", "ginvite", "gkick", "gban", "gunban", 
                   "grole", "grequests", "gaccept", "greject", 
                   "gannounce", "gdelannounce", "gaudit"],
    }
    
    for module_name, cmd_list in modules.items():
        msg += f"【{module_name}】\n"
        for cmd_name in cmd_list:
            cmd_config = config.commands.get(cmd_name)
            if cmd_config:
                status = "✅" if cmd_config.enabled else "❌"
                perm_names = {0: "用户", 1: "管理", 2: "超管"}
                perm = perm_names.get(cmd_config.permission, "?")
                
                # 标记与默认不同的配置
                defaults = COMMAND_DEFAULTS.get(cmd_name, {})
                is_default = (
                    cmd_config.enabled == defaults.get("enabled", True) and
                    cmd_config.permission == defaults.get("permission", PermissionLevel.USER).value
                )
                marker = "" if is_default else " ⚙️"
                
                msg += f"  {status} #{cmd_name} (权限: {perm}){marker}\n"
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
    except (ValueError, KeyError):
        await config_cmd.finish(format_error(
            f"无效的权限等级: {perm_str}",
            "有效值: 0/user, 1/admin, 2/superuser"
        ))
    
    # 不允许降低 bot 命令的权限
    if cmd_name == "bot" and perm_level < PermissionLevel.SUPERUSER:
        await config_cmd.finish(format_error("配置管理命令必须保持超级管理员权限"))
    
    config = group_config_store.get(str(event.group_id))
    config.set_command_permission(cmd_name, perm_level)
    group_config_store.set(config)
    
    perm_names = {0: "普通用户", 1: "群管理员", 2: "超级管理员"}
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
        # 重新初始化会由 model_post_init 自动完成
        group_config_store.set(config)
        
        await config_cmd.finish(format_success("已重置所有命令配置为默认值"))
