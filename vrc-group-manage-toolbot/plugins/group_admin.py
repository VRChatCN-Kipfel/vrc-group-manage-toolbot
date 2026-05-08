from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg, ArgPlainText
from nonebot.typing import T_State

from utils import get_vrc_client, ensure_vrc_auth
from services.api_guard import api_guard
from services.permission import get_permission_level, PermissionLevel, check_command_permission
from services.message_utils import format_success, format_error, send_long_message
from services.group_config import group_config_store


async def require_auth(matcher, client=None):
    c = client or get_vrc_client()
    if not c.config.auth_cookie:
        await matcher.finish("⚠️ 尚未登录 VRChat API\n请先使用 #vrclLogin 或 #vrclLogin cookie=xxx")


def resolve_group_id(text_parts: list, qq_group_id: str) -> str:
    if text_parts and text_parts[0].startswith("grp_"):
        return text_parts[0]
    config = group_config_store.get(qq_group_id)
    return config.default_vrc_group


# ── gmembers ──

gmembers_cmd = on_command("gmembers", priority=5, block=True)


@gmembers_cmd.handle()
async def handle_gmembers(bot: Bot, event: GroupMessageEvent, state: T_State,
                          args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gmembers")
    if not allowed:
        await gmembers_cmd.finish(error_msg)
    
    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    if not group_id:
        await gmembers_cmd.finish(format_error(
            "请提供群组ID",
            "/gmembers grp_xxx 或使用 /bot config 设置默认群组",
        ))

    await require_auth(gmembers_cmd)

    page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1

    await gmembers_cmd.send("正在查询群成员...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.get_group_members,
        group_id,
        n=20,
        offset=(page - 1) * 20,
        _endpoint="get_group_members",
    )

    if not success:
        await gmembers_cmd.finish(format_error(error or "未知错误"))

    members = data
    if not members:
        await gmembers_cmd.finish(f"群组 {group_id} 没有成员")

    msg = f"📋 群组成员 (第{page}页)\n"
    msg += "─" * 24 + "\n"
    for m in members[:20]:
        msg += f"• {m.userId}\n"
        if m.roleIds:
            msg += f"  角色: {', '.join(m.roleIds[:3])}\n"
        msg += "\n"

    if len(members) == 20:
        msg += f"📄 下一页: /gmembers {group_id} {page + 1}"
    else:
        msg += f"共 {len(members)} 人"

    await send_long_message(gmembers_cmd, msg)


# ── ginvite ──

ginvite_cmd = on_command("ginvite", priority=5, block=True)


@ginvite_cmd.handle()
async def handle_ginvite(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "ginvite")
    if not allowed:
        await ginvite_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    user_arg_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= user_arg_idx:
        await ginvite_cmd.finish(format_error(
            "参数不足",
            "用法: /ginvite <群组ID> <用户ID>",
        ))

    user_id = parts[user_arg_idx]

    await ginvite_cmd.send(f"正在邀请 {user_id} 加入群组...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.invite_user_to_group,
        group_id,
        user_id,
        _endpoint="invite_user",
    )

    if success:
        await ginvite_cmd.finish(format_success(f"已向 {user_id} 发出群组邀请"))
    else:
        await ginvite_cmd.finish(format_error(error or "邀请失败"))


# ── gkick ──

gkick_cmd = on_command("gkick", priority=5, block=True)


@gkick_cmd.handle()
async def handle_gkick_pre(bot: Bot, event: GroupMessageEvent, state: T_State,
                           args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gkick")
    if not allowed:
        await gkick_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    user_arg_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= user_arg_idx:
        await gkick_cmd.finish(format_error(
            "参数不足",
            "用法: /gkick <群组ID> <用户ID>",
        ))

    state["group_id"] = group_id
    state["user_id"] = parts[user_arg_idx]


@gkick_cmd.got("confirm", prompt="⚠️ 确认将此用户踢出群组？回复 'yes' 确认，其他任意键取消")
async def handle_gkick_confirm(bot: Bot, event: GroupMessageEvent, state: T_State,
                               confirm: str = ArgPlainText()):
    if confirm.strip().lower() != "yes":
        await gkick_cmd.finish("操作已取消")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.kick_user_from_group,
        state["group_id"],
        state["user_id"],
        _endpoint="kick_group_member",
    )

    if success:
        await gkick_cmd.finish(format_success(f"已将 {state['user_id']} 踢出群组"))
    else:
        await gkick_cmd.finish(format_error(error or "操作失败"))


# ── gban ──

gban_cmd = on_command("gban", priority=5, block=True)


@gban_cmd.handle()
async def handle_gban_pre(bot: Bot, event: GroupMessageEvent, state: T_State,
                          args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gban")
    if not allowed:
        await gban_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    user_arg_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= user_arg_idx:
        await gban_cmd.finish(format_error(
            "参数不足",
            "用法: /gban <群组ID> <用户ID>",
        ))

    state["group_id"] = group_id
    state["user_id"] = parts[user_arg_idx]


@gban_cmd.got("confirm", prompt="⚠️ 确认封禁此用户？回复 'yes' 确认，其他任意键取消")
async def handle_gban_confirm(bot: Bot, event: GroupMessageEvent, state: T_State,
                              confirm: str = ArgPlainText()):
    if confirm.strip().lower() != "yes":
        await gban_cmd.finish("操作已取消")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.ban_user_from_group,
        state["group_id"],
        state["user_id"],
        _endpoint="ban_user",
    )

    if success:
        await gban_cmd.finish(format_success(f"已将 {state['user_id']} 封禁"))
    else:
        await gban_cmd.finish(format_error(error or "操作失败"))


# ── gunban ──

gunban_cmd = on_command("gunban", priority=5, block=True)


@gunban_cmd.handle()
async def handle_gunban(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gunban")
    if not allowed:
        await gunban_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    user_arg_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= user_arg_idx:
        await gunban_cmd.finish(format_error(
            "参数不足",
            "用法: /gunban <群组ID> <用户ID>",
        ))

    user_id = parts[user_arg_idx]

    await gunban_cmd.send(f"正在解封 {user_id}...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.unban_user_from_group,
        group_id,
        user_id,
        _endpoint="unban_user",
    )

    if success:
        await gunban_cmd.finish(format_success(f"已解封 {user_id}"))
    else:
        await gunban_cmd.finish(format_error(error or "操作失败"))


# ── grole ──

grole_cmd = on_command("grole", priority=5, block=True)


@grole_cmd.handle()
async def handle_grole(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "grole")
    if not allowed:
        await grole_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    if len(parts) < 2:
        await grole_cmd.finish(format_error(
            "参数不足",
            "用法: /grole <群组ID> <用户ID> <角色名>",
        ))

    group_id = parts[0] if parts[0].startswith("grp_") else None
    if not group_id:
        config = group_config_store.get(str(event.group_id))
        group_id = config.default_vrc_group
        user_idx = 0
    else:
        user_idx = 1

    if not group_id or len(parts) <= user_idx + 1:
        await grole_cmd.finish(format_error(
            "参数不足",
            "用法: /grole <群组ID> <用户ID> <角色名>",
        ))

    user_id = parts[user_idx]
    role_name = " ".join(parts[user_idx + 1:])

    client = get_vrc_client()

    success, roles, error = await api_guard.call_with_retry(
        client.get_group_roles,
        group_id,
        _endpoint="get_group_roles",
    )

    if not success:
        await grole_cmd.finish(format_error(error or "获取角色列表失败"))

    role_name_lower = role_name.lower()
    matched_role = None
    for role in roles:
        if role_name_lower in role.name.lower() or role.id == role_name:
            matched_role = role
            break

    if not matched_role:
        role_list = "\n".join(f"  • {r.name} ({r.id})" for r in roles)
        await grole_cmd.finish(f"未找到角色 '{role_name}'\n可用角色:\n{role_list}")

    score, data, error = await api_guard.call_with_retry(
        client.update_member_role,
        group_id,
        user_id,
        [matched_role.id],
        _endpoint="update_member_role",
    )

    if score:
        await grole_cmd.finish(format_success(
            f"已将 {user_id} 的角色设置为: {matched_role.name}"
        ))
    else:
        await grole_cmd.finish(format_error(error or "设置角色失败"))


# ── grequests ──

grequests_cmd = on_command("grequests", priority=5, block=True)


@grequests_cmd.handle()
async def handle_grequests(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "grequests")
    if not allowed:
        await grequests_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))

    if not group_id:
        await grequests_cmd.finish(format_error(
            "请提供群组ID",
            "/grequests grp_xxx",
        ))

    await grequests_cmd.send("正在查询入群申请...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.get_group_join_requests,
        group_id,
        _endpoint="get_join_requests",
    )

    if not success:
        await grequests_cmd.finish(format_error(error or "获取申请列表失败"))

    requests_list = data
    if not requests_list:
        await grequests_cmd.finish("当前没有待处理的入群申请")

    msg = f"📋 入群申请 ({len(requests_list)}人)\n"
    msg += "─" * 24 + "\n"
    for i, req in enumerate(requests_list[:20], 1):
        msg += f"{i}. {req.userId}\n"

    if len(requests_list) > 20:
        msg += f"\n... 还有 {len(requests_list) - 20} 条申请"

    await send_long_message(grequests_cmd, msg)


# ── gaccept ──

gaccept_cmd = on_command("gaccept", priority=5, block=True)


@gaccept_cmd.handle()
async def handle_gaccept(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gaccept")
    if not allowed:
        await gaccept_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    user_arg_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= user_arg_idx:
        await gaccept_cmd.finish(format_error(
            "参数不足",
            "用法: /gaccept <群组ID> <用户ID>",
        ))

    user_id = parts[user_arg_idx]

    await gaccept_cmd.send(f"正在批准 {user_id} 的入群申请...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.respond_join_request,
        group_id,
        user_id,
        "accept",
        _endpoint="accept_join_request",
    )

    if success:
        await gaccept_cmd.finish(format_success(f"已批准 {user_id} 加入群组"))
    else:
        await gaccept_cmd.finish(format_error(error or "操作失败"))


# ── greject ──

greject_cmd = on_command("greject", priority=5, block=True)


@greject_cmd.handle()
async def handle_greject(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "greject")
    if not allowed:
        await greject_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    user_arg_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= user_arg_idx:
        await greject_cmd.finish(format_error(
            "参数不足",
            "用法: /greject <群组ID> <用户ID>",
        ))

    user_id = parts[user_arg_idx]

    await greject_cmd.send(f"正在拒绝 {user_id} 的入群申请...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.respond_join_request,
        group_id,
        user_id,
        "reject",
        _endpoint="reject_join_request",
    )

    if success:
        await greject_cmd.finish(format_success(f"已拒绝 {user_id} 的入群申请"))
    else:
        await greject_cmd.finish(format_error(error or "操作失败"))


# ── gannounce ──

gannounce_cmd = on_command("gannounce", priority=5, block=True)


@gannounce_cmd.handle()
async def handle_gannounce_pre(bot: Bot, event: GroupMessageEvent, state: T_State,
                               args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gannounce")
    if not allowed:
        await gannounce_cmd.finish(error_msg)

    text = args.extract_plain_text().strip()
    lines = text.split("\n", 1)

    if len(lines) < 2:
        await gannounce_cmd.finish(format_error(
            "参数不足",
            "用法: /gannounce <群组ID>\n<标题>\n<内容>",
        ))

    group_id = lines[0].strip().split()[0] if lines[0].strip() else ""
    title_line = lines[0].strip()
    remaining = lines[1] if len(lines) > 1 else ""

    if group_id.startswith("grp_"):
        title = title_line[len(group_id):].strip() if title_line.startswith(group_id) else title_line
        content = remaining
    else:
        config = group_config_store.get(str(event.group_id))
        group_id = config.default_vrc_group
        title = title_line
        content = remaining

    if not group_id:
        await gannounce_cmd.finish(format_error(
            "请提供群组ID",
            "/gannounce grp_xxx\n标题\n内容",
        ))

    if not title:
        await gannounce_cmd.finish(format_error("请提供公告标题"))

    if not content:
        await gannounce_cmd.finish(format_error("请提供公告内容"))

    state["group_id"] = group_id
    state["title"] = title
    state["content"] = content
    await gannounce_cmd.send(f"⚠️ 确认发布此公告？\n标题: {title}\n内容: {content}\n\n回复 'yes' 确认，其他任意键取消")


@gannounce_cmd.got("confirm")
async def handle_gannounce_confirm(bot: Bot, event: GroupMessageEvent, state: T_State,
                                   confirm: str = ArgPlainText()):
    if confirm.strip().lower() != "yes":
        await gannounce_cmd.finish("操作已取消")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.create_group_announcement,
        state["group_id"],
        state["title"],
        state["content"],
        _endpoint="create_announcement",
    )

    if success:
        await gannounce_cmd.finish(format_success("公告已发布"))
    else:
        await gannounce_cmd.finish(format_error(error or "发布公告失败"))


# ── gdelannounce ──

gdelannounce_cmd = on_command("gdelannounce", priority=5, block=True)


@gdelannounce_cmd.handle()
async def handle_gdelannounce_pre(bot: Bot, event: GroupMessageEvent, state: T_State,
                                  args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gdelannounce")
    if not allowed:
        await gdelannounce_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))
    ann_id_idx = 1 if (parts and parts[0].startswith("grp_")) else 0

    if not group_id or len(parts) <= ann_id_idx:
        await gdelannounce_cmd.finish(format_error(
            "参数不足",
            "用法: /gdelannounce <群组ID> <公告ID>",
        ))

    state["group_id"] = group_id
    state["announcement_id"] = parts[ann_id_idx]


@gdelannounce_cmd.got("confirm",
                      prompt="⚠️ 确认删除此公告？回复 'yes' 确认，其他任意键取消")
async def handle_gdelannounce_confirm(bot: Bot, event: GroupMessageEvent, state: T_State,
                                      confirm: str = ArgPlainText()):
    if confirm.strip().lower() != "yes":
        await gdelannounce_cmd.finish("操作已取消")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.delete_group_announcement,
        state["group_id"],
        state["announcement_id"],
        _endpoint="delete_announcement",
    )

    if success:
        await gdelannounce_cmd.finish(format_success("公告已删除"))
    else:
        await gdelannounce_cmd.finish(format_error(error or "删除公告失败"))


# ── gaudit ──

gaudit_cmd = on_command("gaudit", priority=5, block=True)


@gaudit_cmd.handle()
async def handle_gaudit(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查权限
    allowed, error_msg = await check_command_permission(bot, event, "gaudit")
    if not allowed:
        await gaudit_cmd.finish(error_msg)

    parts = args.extract_plain_text().strip().split()
    group_id = resolve_group_id(parts, str(event.group_id))

    if not group_id:
        await gaudit_cmd.finish(format_error(
            "请提供群组ID",
            "/gaudit grp_xxx",
        ))

    await gaudit_cmd.send("正在查询审核日志...")

    client = get_vrc_client()
    success, data, error = await api_guard.call_with_retry(
        client.get_group_audit_logs,
        group_id,
        n=50,
        _endpoint="get_audit_logs",
    )

    if not success:
        await gaudit_cmd.finish(format_error(error or "获取审核日志失败"))

    logs = data
    if not logs:
        await gaudit_cmd.finish("暂无审核日志")

    msg = "📋 审核日志 (最近50条)\n"
    msg += "─" * 24 + "\n"
    for log_entry in logs[:20]:
        desc = log_entry.description or "无描述"
        created = log_entry.created_at or ""
        msg += f"• {desc}\n"
        if created:
            msg += f"  时间: {created}\n"
        msg += "\n"

    if len(logs) > 20:
        msg += f"... 还有 {len(logs) - 20} 条日志"

    await send_long_message(gaudit_cmd, msg)
