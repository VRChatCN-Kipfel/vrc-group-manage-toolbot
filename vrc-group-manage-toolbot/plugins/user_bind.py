import secrets
import string
import time
from typing import Optional

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg, ArgPlainText
from nonebot.typing import T_State

from utils import get_vrc_client, check_vrc_auth
from services.api_guard import api_guard
from services.permission import get_permission_level, PermissionLevel
from services.user_binding import user_binding_store, BindingRecord
from services.message_utils import format_success, format_error, send_long_message


def generate_verify_code(length: int = 6) -> str:
    return ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )


def extract_at_qq(msg: Message) -> Optional[str]:
    for seg in msg:
        if seg.type == "at":
            qq = seg.data.get("qq", "")
            if qq and qq != "all":
                return str(qq)
    return None


# ── /bind ──

bind_cmd = on_command("bind", priority=5, block=True)


@bind_cmd.handle()
async def handle_bind(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    text = args.extract_plain_text().strip()
    raw_msg = event.get_message()

    if text.startswith("force"):
        level = await get_permission_level(bot, event)
        if level < PermissionLevel.SUPERUSER:
            await bind_cmd.finish(format_error("强制绑定需要机器人超级管理员权限"))

        at_qq = extract_at_qq(raw_msg)
        rest = text[5:].strip()
        vrc_id = rest.split()[-1] if rest else ""

        if not at_qq or not (vrc_id.startswith("usr_") if vrc_id else False):
            await bind_cmd.finish(format_error(
                "参数不正确",
                "用法: /bind force @某人 usr_xxxx",
            ))

        client = get_vrc_client()
        err = check_vrc_auth(client)
        if err:
            await bind_cmd.finish(err)
            return
        success, user, error = await api_guard.call_with_retry(
            client.get_user, vrc_id, _endpoint="get_user",
        )
        if not success or not user:
            await bind_cmd.finish(format_error(
                f"找不到 VRChat 用户: {vrc_id}",
                "请检查用户 ID 是否正确",
            ))

        binding = BindingRecord(
            qq_id=at_qq,
            vrc_user_id=user.id,
            vrc_display_name=user.displayName,
            bound_at=time.time(),
            confirmed=True,
        )
        user_binding_store.set(binding)
        await bind_cmd.finish(format_success(
            f"已强制绑定: @{at_qq} -> {user.displayName} ({user.id})"
        ))
        return

    vrc_id = text.split()[0] if text else ""

    if not vrc_id or not vrc_id.startswith("usr_"):
        await bind_cmd.finish(format_error(
            "请提供你的 VRChat 用户 ID",
            "用法: /bind usr_xxxx (以 usr_ 开头)",
        ))

    existing = user_binding_store.get_by_qq(str(event.user_id))
    if existing and existing.confirmed:
        await bind_cmd.finish(format_error(
            f"你已经绑定了 {existing.vrc_display_name} ({existing.vrc_user_id})",
            "如需更换绑定，请先 /unbind",
        ))

    client = get_vrc_client()
    success, user, error = await api_guard.call_with_retry(
        client.get_user, vrc_id, _endpoint="get_user",
    )
    if not success or not user:
        await bind_cmd.finish(format_error(
            f"找不到 VRChat 用户: {vrc_id}",
            "请检查用户 ID 是否正确",
        ))

    already_bound = user_binding_store.get_by_vrc(vrc_id)
    if already_bound:
        await bind_cmd.finish(format_error(
            f"该 VRChat 账号已被 QQ {already_bound.qq_id} 绑定",
            "如果是你的账号被冒绑，联系管理员使用 /bind force",
        ))

    code = generate_verify_code()

    pending = BindingRecord(
        qq_id=str(event.user_id),
        vrc_user_id=user.id,
        vrc_display_name=user.displayName,
        bound_at=time.time(),
        confirmed=False,
        verify_code=code,
        verify_code_expires=time.time() + 180,
    )
    user_binding_store.set(pending)

    await bind_cmd.finish(
        f"🔐 身份验证\n\n"
        f"1. 请在 VRChat 中修改你的 Bio（个人简介），\n"
        f"   在任意位置添加: [VRCBOT:{code}]\n\n"
        f"2. 完成后在 3 分钟内发送 /confirm\n\n"
        f"绑定目标: {user.displayName} ({user.id})"
    )


# ── /confirm ──

confirm_cmd = on_command("confirm", priority=5, block=True)


@confirm_cmd.handle()
async def handle_confirm(bot: Bot, event: GroupMessageEvent):
    qq_id = str(event.user_id)

    pending = user_binding_store.get_by_qq(qq_id)
    if not pending:
        await confirm_cmd.finish(format_error(
            "没有待确认的绑定",
            "请先使用 /bind <你的VRChat用户ID>",
        ))

    if pending.confirmed:
        await confirm_cmd.finish(format_success(
            f"你已绑定: {pending.vrc_display_name} ({pending.vrc_user_id})"
        ))

    if time.time() > (pending.verify_code_expires or 0):
        user_binding_store.remove(qq_id)
        await confirm_cmd.finish(format_error(
            "验证码已过期（超过3分钟）",
            "请重新 /bind",
        ))

    await confirm_cmd.send("正在验证 Bio...")

    client = get_vrc_client()
    success, user, error = await api_guard.call_with_retry(
        client.get_user, pending.vrc_user_id, _endpoint="get_user",
    )
    if not success or not user:
        await confirm_cmd.finish(format_error(
            "无法获取 VRChat 用户信息",
            "稍后重试或检查用户是否存在",
        ))

    user_bio = user.bio or ""
    expected_marker = f"VRCBOT:{pending.verify_code}"
    bio_upper = user_bio.upper()
    code_upper = (pending.verify_code or "").upper()

    if expected_marker.upper() not in bio_upper and code_upper not in bio_upper:
        await confirm_cmd.finish(format_error(
            "Bio 验证失败，未找到验证码",
            f"请确保 Bio 中包含 [VRCBOT:{pending.verify_code}]，然后重新 /confirm",
        ))

    pending.confirmed = True
    pending.verify_code = None
    pending.verify_code_expires = None
    pending.bound_at = time.time()
    user_binding_store.set(pending)

    await confirm_cmd.finish(format_success(
        f"绑定成功！{pending.vrc_display_name} ({pending.vrc_user_id}) <-> QQ {qq_id}"
    ))


# ── /unbind ──

unbind_cmd = on_command("unbind", priority=5, block=True)


@unbind_cmd.handle()
async def handle_unbind_pre(bot: Bot, event: GroupMessageEvent, state: T_State):
    binding = user_binding_store.get_by_qq(str(event.user_id))
    if not binding:
        await unbind_cmd.finish(format_error(
            "你还没有绑定 VRChat 账号",
            "使用 /bind <你的VRChat用户ID> 进行绑定",
        ))

    state["vrc_name"] = binding.vrc_display_name
    state["vrc_id"] = binding.vrc_user_id
    await unbind_cmd.send(f"⚠️ 确认解绑 {binding.vrc_display_name} ({binding.vrc_user_id})？回复 'yes' 确认，其他任意键取消")


@unbind_cmd.got("confirm")
async def handle_unbind_confirm(event: GroupMessageEvent, state: T_State,
                                confirm: str = ArgPlainText()):
    if confirm.strip().lower() != "yes":
        await unbind_cmd.finish("操作已取消")

    user_binding_store.remove(str(event.user_id))
    await unbind_cmd.finish(format_success("已解绑"))


# ── /bindinfo ──

bindinfo_cmd = on_command("bindinfo", priority=5, block=True)


@bindinfo_cmd.handle()
async def handle_bindinfo(bot: Bot, event: GroupMessageEvent):
    raw_msg = event.get_message()
    at_qq = extract_at_qq(raw_msg)

    target_qq = at_qq or str(event.user_id)
    binding = user_binding_store.get_by_qq(target_qq)

    if not binding:
        if not at_qq:
            await bindinfo_cmd.finish(format_error(
                "你还没有绑定 VRChat 账号",
                "使用 /bind <你的VRChat用户ID> 进行绑定",
            ))
        else:
            await bindinfo_cmd.finish("该用户尚未绑定 VRChat 账号")

    source = "你" if target_qq == str(event.user_id) else f"QQ {target_qq}"
    status = "✅ 已确认" if binding.confirmed else "⏳ 待验证"

    msg = f"🔗 绑定信息\n"
    msg += "─" * 20 + "\n"
    msg += f"来源: {source}\n"
    msg += f"VRChat: {binding.vrc_display_name}\n"
    msg += f"ID: {binding.vrc_user_id}\n"
    msg += f"状态: {status}\n"

    await bindinfo_cmd.finish(msg)


# ── /whois ──

whois_cmd = on_command("whois", priority=5, block=True)


@whois_cmd.handle()
async def handle_whois(bot: Bot, event: GroupMessageEvent):
    raw_msg = event.get_message()
    at_qq = extract_at_qq(raw_msg)

    if not at_qq:
        await whois_cmd.finish(format_error(
            "请 @ 你要查询的人",
            "用法: /whois @某人",
        ))

    binding = user_binding_store.get_by_qq(at_qq)
    if not binding:
        await whois_cmd.finish(f"QQ {at_qq} 尚未绑定 VRChat 账号")

    await whois_cmd.send(f"正在查询 {binding.vrc_display_name} 的状态...")

    client = get_vrc_client()
    success, user, error = await api_guard.call_with_retry(
        client.get_user, binding.vrc_user_id, _endpoint="get_user",
    )

    if not success or not user:
        await whois_cmd.finish(format_error(error or "无法获取用户信息"))

    msg = f"👤 {user.displayName}\n"
    msg += "─" * 20 + "\n"
    msg += f"状态: {user.status or '离线'}\n"

    if user.location and user.location != "offline":
        msg += f"位置: {user.location}\n"

        if ":" in user.location:
            location_parts = user.location.split(":")
            if len(location_parts) >= 2:
                world_id = location_parts[0]
                instance_tag = location_parts[1].split("~")[0]
                instance_id = f"{world_id}:{instance_tag}"

                inst_success, instance, _ = await api_guard.call_with_retry(
                    client.get_instance, instance_id, _endpoint="get_instance",
                )
                if inst_success and instance:
                    msg += f"世界: {instance.worldName or '未知'}\n"
                    msg += f"人数: {instance.userCount}/{instance.capacity}\n"
    else:
        msg += "位置: 离线或隐藏\n"

    await whois_cmd.finish(msg)
