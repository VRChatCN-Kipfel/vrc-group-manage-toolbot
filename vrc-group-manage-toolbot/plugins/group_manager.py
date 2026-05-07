"""
群组实例管理插件
提供查询群组实例、用户状态等功能
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message
from nonebot.params import CommandArg

from utils import get_vrc_client, check_vrc_auth
from services.api_guard import api_guard
from services.message_utils import format_error


# 创建命令处理器
group_instances = on_command("instances", priority=5)
user_location = on_command("whereis", priority=5)

# 登录命令


@group_instances.handle()
async def handle_group_instances(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    """
    查询群组的活跃实例
    用法: /instances <group_id>
    """
    group_id = args.extract_plain_text().strip()
    
    if not group_id:
        await group_instances.finish("请提供群组 ID\n用法: /instances grp_xxx")
    
    await group_instances.send("正在查询群组实例...")

    msg = ""
    client = get_vrc_client()
    err = check_vrc_auth(client)
    if err:
        await group_instances.finish(err)
        return

    await group_instances.send("正在查询群组实例...")

    try:
        success, group, err = await api_guard.call_with_retry(
            client.get_group, group_id, _endpoint="get_group")
        if not success or not group:
            msg = format_error(err or f"无法获取群组信息: {group_id}")
        else:
            success2, instances, err2 = await api_guard.call_with_retry(
                client.get_group_instances, group_id, _endpoint="get_group_instances")
            if not success2:
                msg = format_error(err2 or "获取实例列表失败")
            elif not instances:
                msg = f"群组: {group.name}\n当前没有活跃实例"
            else:
                msg = f"群组: {group.name}\n"
                msg += f"成员数: {group.memberCount or 'N/A'}\n"
                msg += f"在线成员: {group.onlineMemberCount or 'N/A'}\n\n"
                msg += f"活跃实例 ({len(instances)}个):\n\n"
                for i, inst in enumerate(instances[:10], 1):
                    msg += f"{i}. {inst.worldId or '未知世界'}\n"
                    msg += f"   人数: {inst.display_count}\n"
                if len(instances) > 10:
                    msg += f"... 还有 {len(instances) - 10} 个实例"
    except Exception as e:
        logger.error(f"查询群组实例失败: {e}")
        msg = f"查询失败: {str(e)}"

    await group_instances.finish(msg)


@user_location.handle()
async def handle_user_location(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    """
    查询用户当前位置
    用法: /whereis <user_id>
    """
    user_id = args.extract_plain_text().strip()
    
    if not user_id:
        await user_location.finish("请提供用户 ID\n用法: /whereis usr_xxx")
    
    await user_location.send("正在查询用户位置...")

    msg = ""
    client = get_vrc_client()
    err = check_vrc_auth(client)
    if err:
        await user_location.finish(err)
        return

    await user_location.send("正在查询用户位置...")

    try:
        success, user, err = await api_guard.call_with_retry(
            client.get_user, user_id, _endpoint="get_user")
        if not success or not user:
            msg = format_error(err or f"无法获取用户信息: {user_id}")
        else:
            msg = f"用户: {user.displayName}\n"
            msg += f"状态: {user.status or '离线'}\n"
            if user.location and user.location != "offline":
                msg += f"位置: {user.location}\n"
                if ":" in user.location:
                    location_parts = user.location.split(":")
                    if len(location_parts) >= 2:
                        world_id = location_parts[0]
                        instance_tag = location_parts[1].split("~")[0]
                        instance_id = f"{world_id}:{instance_tag}"
                        inst_ok, instance, _ = await api_guard.call_with_retry(
                            client.get_instance, instance_id, _endpoint="get_instance")
                        if inst_ok and instance:
                            msg += f"世界: {instance.worldName or '未知'}\n"
                            msg += f"人数: {instance.userCount}/{instance.capacity}\n"
            else:
                msg += "位置: 离线或隐藏"
    except Exception as e:
        logger.error(f"查询用户位置失败: {e}")
        msg = f"查询失败: {str(e)}"

    await user_location.finish(msg)


# 登录命令
vrc_login = on_command("vrclLogin", priority=5)

# 两步验证命令
vrc_2fa = on_command("2fa", priority=5)

_pending_2fa: bool = False


@vrc_login.handle()
async def handle_vrc_login(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    global _pending_2fa

    text = args.extract_plain_text().strip()

    # Cookie 直登
    if text.startswith("cookie="):
        cookie = text[7:].strip()
        if not cookie:
            await vrc_login.finish("用法: #vrclLogin cookie=authcookie_xxxx")
            return
        if cookie.startswith("auth="):
            cookie = cookie[5:]

        await vrc_login.send("正在验证 Cookie...")
        user = None
        try:
            client = get_vrc_client()
            client.config.auth_cookie = cookie
            client.client = None
            client._authenticated = False
            logger.info(f"Trying cookie login, cookie len={len(cookie)}")
            user = await client.get_current_user()
        except Exception as e:
            logger.error(f"Cookie 验证异常: {e}")
            client.config.auth_cookie = None
            client.client = None

        if user:
            client._authenticated = True
            client._save_cookie()
            await vrc_login.finish(f"登录成功！欢迎, {user.displayName}")
        else:
            client.config.auth_cookie = None
            client.client = None
            await vrc_login.finish("Cookie 无效或已过期（请确认复制的是 'auth' 这一行的 Value 值）")
        return

    # 正常登录
    await vrc_login.send("正在登录 VRChat API...")

    try:
        client = get_vrc_client()
        result = await client.login()
    except Exception as e:
        logger.error(f"VRChat 登录异常: {e}")
        await vrc_login.finish(f"登录失败: {str(e)}")
        return

    if result == "need_2fa":
        _pending_2fa = True
        await vrc_login.send("⚠️ 需要两步验证 (TOTP)，请在 30 秒内使用 #2fa <6位验证码>")
        await vrc_login.finish()
        return

    await _finish_login(vrc_login, get_vrc_client(), result)


@vrc_2fa.handle()
async def handle_vrc_2fa(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    global _pending_2fa

    if not _pending_2fa:
        await vrc_2fa.finish("当前没有待处理的两步验证，请先使用 #vrclLogin")
        return

    code = args.extract_plain_text().strip()
    if len(code) != 6 or not code.isdigit():
        await vrc_2fa.finish("验证码应为 6 位数字（如 #2fa 123456）")
        return

    await vrc_2fa.send(f"正在验证两步验证码: {code}...")

    try:
        client = get_vrc_client()
        result = await client.verify_2fa(code)
    except Exception as e:
        logger.error(f"VRChat 两步验证异常: {e}")
        _pending_2fa = False
        await vrc_2fa.finish(f"验证失败: {str(e)}")
        return

    _pending_2fa = False
    if result is True:
        await _finish_login(vrc_2fa, get_vrc_client(), True)
    else:
        await vrc_2fa.send("❌ 验证码错误或已过期，请重新 #vrclLogin 获取新验证码")


async def _finish_login(matcher, client, result):
    if result is True:
        try:
            user = await client.get_current_user()
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            await matcher.finish("登录成功但无法获取用户信息")
            return
        if user:
            await matcher.finish(f"登录成功！欢迎, {user.displayName}")
        else:
            await matcher.finish("登录成功但无法获取用户信息")
    else:
        await matcher.finish("登录失败，请检查 .env 中的配置")
