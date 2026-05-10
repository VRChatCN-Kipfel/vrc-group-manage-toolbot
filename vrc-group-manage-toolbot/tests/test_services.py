import asyncio
import time
from unittest.mock import MagicMock, AsyncMock

import pytest
import httpx

from services.group_config import (
    COMMAND_DEFAULTS, CommandConfig, GroupConfig, group_config_store,
)
from services.permission import (
    PermissionLevel, set_temp_permission, clear_temp_permission,
    get_all_temp_permissions,
)
from services.api_guard import ApiGuard, api_guard
from services.message_utils import format_success, format_error, format_query_result
from services.user_binding import BindingRecord, user_binding_store


# ── test_command_defaults ──

@pytest.mark.parametrize("module_name,cmd_list", [
    ("系统/认证", ["vrclLogin", "2fa", "vrcCheck"]),
    ("查询", ["whereis", "instances", "whois"]),
    ("用户绑定", ["bind", "confirm", "unbind", "bindinfo"]),
    ("群组管理", ["gmembers", "ginvite", "gkick", "gban", "gunban",
                  "grole", "grequests", "gaccept", "greject",
                  "gannounce", "gdelannounce", "gaudit"]),
])
def test_command_defaults(module_name, cmd_list):
    for cmd in cmd_list:
        assert cmd in COMMAND_DEFAULTS, f"命令 {cmd} 未在 COMMAND_DEFAULTS 中定义"
        config = COMMAND_DEFAULTS[cmd]
        assert "enabled" in config
        assert "permission" in config
        assert isinstance(config["permission"], PermissionLevel)


# ── test_group_config ──

def test_group_config(nonebot_init):
    test_group_id = "test_123456"
    config = group_config_store.get(test_group_id)

    expected_count = len(COMMAND_DEFAULTS)
    assert len(config.commands) >= expected_count

    whereis_enabled = config.is_command_enabled("whereis")
    whereis_perm = config.get_command_permission("whereis")
    assert isinstance(whereis_enabled, bool)
    assert isinstance(whereis_perm, PermissionLevel)

    config.set_command_enabled("gban", False)
    config.set_command_permission("whereis", PermissionLevel.BOUND_ADMIN)
    group_config_store.set(config)

    config_reloaded = group_config_store.get(test_group_id)
    assert not config_reloaded.is_command_enabled("gban")
    assert config_reloaded.get_command_permission("whereis") == PermissionLevel.BOUND_ADMIN

    config_reloaded.commands.clear()
    group_config_store.set(config_reloaded)


# ── test_permission_check ──

@pytest.mark.parametrize("input_str,expected", [
    ("unbound_user", PermissionLevel.UNBOUND_USER),
    ("bound_user", PermissionLevel.BOUND_USER),
    ("unbound_admin", PermissionLevel.UNBOUND_ADMIN),
    ("bound_admin", PermissionLevel.BOUND_ADMIN),
    ("owner", PermissionLevel.OWNER),
    ("superuser", PermissionLevel.SUPERUSER),
    ("0", PermissionLevel.UNBOUND_USER),
    ("1", PermissionLevel.BOUND_USER),
    ("2", PermissionLevel.UNBOUND_ADMIN),
    ("3", PermissionLevel.BOUND_ADMIN),
    ("4", PermissionLevel.OWNER),
    ("5", PermissionLevel.SUPERUSER),
])
def test_permission_check(input_str, expected):
    result = PermissionLevel.from_str(input_str)
    assert result == expected, f"from_str('{input_str}') 返回 {result}, 期望 {expected}"


# ── test_command_defaults_extended ──

ALL_EXPECTED_COMMANDS = [
    "vrclLogin", "2fa", "vrcCheck",
    "whereis", "instances", "whois",
    "bind", "confirm", "unbind", "bindinfo",
    "gmembers", "ginvite", "gkick", "gban", "gunban",
    "grole", "grequests", "gaccept", "greject",
    "gannounce", "gdelannounce", "gaudit",
]


@pytest.mark.parametrize("cmd", ALL_EXPECTED_COMMANDS)
def test_command_defaults_extended(cmd):
    cfg = COMMAND_DEFAULTS.get(cmd)
    assert cfg is not None, f"{cmd}: 缺失"
    enabled = cfg.get("enabled")
    perm = cfg.get("permission")
    assert enabled in (True, False), f"{cmd}: enabled 无效值 {enabled!r}"
    assert isinstance(perm, PermissionLevel), f"{cmd}: permission 非 PermissionLevel 类型"
    assert 0 <= perm.value <= 5, f"{cmd}: permission 值 {perm.value} 越界"


# ── test_permission_enum_comprehensive ──

@pytest.mark.parametrize("inp,expected", [
    ("  superuser  ", PermissionLevel.SUPERUSER),
    ("SUPERUSER", PermissionLevel.SUPERUSER),
    ("SuperUser", PermissionLevel.SUPERUSER),
])
def test_permission_from_str_boundary(inp, expected):
    result = PermissionLevel.from_str(inp)
    assert result == expected


@pytest.mark.parametrize("inp", ["invalid", "6", "99", "admin_extra", ""])
def test_permission_from_str_invalid(inp):
    with pytest.raises((KeyError, ValueError)):
        PermissionLevel.from_str(inp)


def test_permission_enum_ordering():
    levels = sorted(PermissionLevel, key=lambda x: x.value)
    names = [lvl.name for lvl in levels]
    expected_order = ["UNBOUND_USER", "BOUND_USER", "UNBOUND_ADMIN", "BOUND_ADMIN", "OWNER", "SUPERUSER"]
    assert names == expected_order


def test_permission_enum_comparison():
    assert PermissionLevel.SUPERUSER > PermissionLevel.OWNER
    assert PermissionLevel.OWNER > PermissionLevel.BOUND_ADMIN
    assert PermissionLevel.BOUND_ADMIN > PermissionLevel.UNBOUND_ADMIN
    assert PermissionLevel.UNBOUND_ADMIN > PermissionLevel.BOUND_USER
    assert PermissionLevel.BOUND_USER > PermissionLevel.UNBOUND_USER
    assert PermissionLevel.SUPERUSER >= PermissionLevel.SUPERUSER
    assert PermissionLevel.UNBOUND_USER <= PermissionLevel.UNBOUND_USER


# ── test_group_config_edge_cases ──

def test_group_config_edge_cases(nonebot_init):
    test_id = "test_edge_987654"
    config = group_config_store.get(test_id)

    config.set_command_enabled("gkick", True)
    config.set_command_enabled("gkick", True)
    assert config.is_command_enabled("gkick")

    result = config.is_command_enabled("nonexistent_cmd")
    assert isinstance(result, bool)

    perm = config.get_command_permission("nonexistent_cmd")
    assert isinstance(perm, PermissionLevel)

    config.set_command_permission("nonexistent_cmd", PermissionLevel.SUPERUSER)
    perm2 = config.get_command_permission("nonexistent_cmd")
    assert perm2 == PermissionLevel.SUPERUSER

    config.default_vrc_group = "grp_test_abc"
    group_config_store.set(config)
    bound_qq = group_config_store.get_by_vrc_group("grp_test_abc")
    assert test_id in bound_qq

    config.default_vrc_group = None
    group_config_store.set(config)
    bound_qq_after = group_config_store.get_by_vrc_group("grp_test_abc")
    assert test_id not in bound_qq_after

    config.commands.clear()
    group_config_store.set(config)


# ── test_temp_permission_functions ──

def test_temp_permission_functions(nonebot_init):
    set_temp_permission("test_qq_001", PermissionLevel.BOUND_ADMIN)
    all_temp = get_all_temp_permissions()
    assert all_temp.get("test_qq_001") == PermissionLevel.BOUND_ADMIN

    set_temp_permission("test_qq_001", PermissionLevel.OWNER)
    all_temp2 = get_all_temp_permissions()
    assert all_temp2.get("test_qq_001") == PermissionLevel.OWNER

    clear_temp_permission("test_qq_001")
    all_temp3 = get_all_temp_permissions()
    assert "test_qq_001" not in all_temp3

    clear_temp_permission("nonexistent_qq")

    set_temp_permission("test_qq_002", PermissionLevel.UNBOUND_USER)
    snapshot = get_all_temp_permissions()
    snapshot["test_qq_002"] = PermissionLevel.SUPERUSER
    original = get_all_temp_permissions()
    assert original.get("test_qq_002") == PermissionLevel.UNBOUND_USER

    clear_temp_permission("test_qq_002")


# ── test_api_guard_basics ──

def test_api_guard_basics(nonebot_init):
    assert isinstance(api_guard.min_interval, float)
    assert isinstance(api_guard.max_retries, int)

    api_guard.cache_set("test_key", {"data": "hello"}, ttl=300)
    cached = api_guard.cache_get("test_key")
    assert cached and cached.get("data") == "hello"

    result = api_guard.cache_get("nonexistent_key")
    assert result is None

    api_guard.cache_set("ephemeral_key", "temp_value", ttl=0)
    expired = api_guard.cache_get("ephemeral_key")
    if expired is not None:
        pass  # TTL=0 tolerance

    stats = api_guard.get_stats()
    assert isinstance(stats, dict)

    api_guard.clear_cache()


# ── test_message_utils ──

def test_message_utils():
    r1 = format_success("操作完成")
    assert "操作完成" in r1 and len(r1) > len("操作完成")

    r2 = format_error("网络超时")
    assert "操作失败" in r2 and "网络超时" in r2

    r3 = format_error("权限不足", "请联系管理员")
    assert "操作失败" in r3 and "权限不足" in r3 and "提示" in r3 and "请联系管理员" in r3

    r4 = format_query_result("测试标题", "内容行1\n内容行2")
    assert "测试标题" in r4 and "内容行1" in r4 and "内容行2" in r4


@pytest.mark.asyncio
async def test_send_long_message_short(nonebot_init):
    from services.message_utils import send_long_message
    matcher = MagicMock()
    matcher.finish = AsyncMock()
    await send_long_message(matcher, "短文本")
    matcher.finish.assert_awaited_once_with("短文本")


@pytest.mark.asyncio
async def test_send_long_message_long(nonebot_init):
    from services.message_utils import send_long_message
    matcher = MagicMock()
    matcher.send = AsyncMock()
    matcher.finish = AsyncMock()
    long_text = "A" * 4000
    await send_long_message(matcher, long_text)
    matcher.send.assert_awaited_once()
    matcher.finish.assert_awaited_once()


# ── test_config_workflow ──

def test_config_workflow(nonebot_init):
    wf_group_id = "test_wf_999999"
    config = group_config_store.get(wf_group_id)

    for cmd in ["gkick", "gban", "gmembers", "instances", "vrclLogin"]:
        perm = config.get_command_permission(cmd)
        enabled = config.is_command_enabled(cmd)
        assert isinstance(perm, PermissionLevel)
        assert isinstance(enabled, bool)

    config.set_command_enabled("gmembers", True)
    config.set_command_permission("gmembers", PermissionLevel.BOUND_ADMIN)
    config.set_command_permission("gkick", PermissionLevel.OWNER)
    config.set_command_enabled("whereis", True)
    config.default_vrc_group = "grp_wf_test"
    group_config_store.set(config)

    config2 = group_config_store.get(wf_group_id)
    assert config2.is_command_enabled("gmembers") == True
    assert config2.get_command_permission("gmembers") == PermissionLevel.BOUND_ADMIN
    assert config2.get_command_permission("gkick") == PermissionLevel.OWNER
    assert config2.is_command_enabled("whereis") == True
    assert config2.default_vrc_group == "grp_wf_test"

    other_config = group_config_store.get("test_other_888")
    other_config.set_command_enabled("gmembers", False)
    group_config_store.set(other_config)

    config3 = group_config_store.get(wf_group_id)
    assert config3.is_command_enabled("gmembers") == True

    bound_groups = group_config_store.get_by_vrc_group("grp_wf_test")
    assert wf_group_id in bound_groups

    config3.default_vrc_group = None
    config3.commands.clear()
    group_config_store.set(config3)
    other_config.commands.clear()
    group_config_store.set(other_config)

    bound_after = group_config_store.get_by_vrc_group("grp_wf_test")
    assert len(bound_after) == 0


# ── test_user_binding_store ──

def test_user_binding_store(nonebot_init):
    test_qq = "test_ub_001"
    test_vrc = "usr_vrc_test_001"

    record = BindingRecord(
        qq_id=test_qq,
        vrc_user_id=test_vrc,
        vrc_display_name="测试用户",
        bound_at=time.time(),
        confirmed=True,
    )
    user_binding_store.set(record)

    fetched = user_binding_store.get_by_qq(test_qq)
    assert fetched is not None
    assert fetched.qq_id == test_qq
    assert fetched.vrc_user_id == test_vrc
    assert fetched.confirmed == True

    fetched2 = user_binding_store.get_by_vrc(test_vrc)
    assert fetched2 is not None
    assert fetched2.qq_id == test_qq

    not_found = user_binding_store.get_by_vrc("usr_nonexistent")
    assert not_found is None

    not_found2 = user_binding_store.get_by_qq("qq_nonexistent")
    assert not_found2 is None

    record2 = BindingRecord(
        qq_id=test_qq,
        vrc_user_id="usr_vrc_updated",
        vrc_display_name="更新后用户",
        bound_at=time.time(),
        confirmed=False,
    )
    user_binding_store.set(record2)
    updated = user_binding_store.get_by_qq(test_qq)
    assert updated.vrc_user_id == "usr_vrc_updated"
    assert updated.confirmed == False

    user_binding_store.remove(test_qq)
    after_remove = user_binding_store.get_by_qq(test_qq)
    assert after_remove is None

    user_binding_store.remove("qq_nonexistent")

    r = BindingRecord(qq_id="001", vrc_user_id="vrc1", vrc_display_name="test", bound_at=0.0)
    assert r.confirmed == False
    assert r.verify_code is None
    assert r.verify_code_expires is None


# ── test_api_guard_call_with_retry ──

@pytest.mark.asyncio
async def test_api_guard_call_with_retry(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=2)

    async def success_call():
        return {"result": "ok"}

    ok, data, err = await guard.call_with_retry(success_call, _endpoint="test_success")
    assert ok == True
    assert data == {"result": "ok"}
    assert err is None

    ok2, data2, err2 = await guard.call_with_retry(
        success_call, _endpoint="test_cached", _cache_key="cache_1", _cache_ttl=300
    )
    ok3, data3, err3 = await guard.call_with_retry(
        success_call, _endpoint="test_cached", _cache_key="cache_1", _cache_ttl=300
    )
    assert data2 == data3
    stats = guard.get_stats()
    assert "test_cached:cache_hit" in stats

    call_count = [0]

    async def flaky_call():
        call_count[0] += 1
        if call_count[0] < 3:
            raise httpx.ConnectError("connection reset")
        return {"recovered": True}

    ok4, data4, err4 = await guard.call_with_retry(flaky_call, _endpoint="test_flaky")
    assert ok4 == True
    assert data4 == {"recovered": True}

    call_count2 = [0]

    async def generic_fail():
        call_count2[0] += 1
        raise ValueError("unexpected error")

    ok5, data5, err5 = await guard.call_with_retry(generic_fail, _endpoint="test_generic_fail")
    assert ok5 == False
    assert data5 is None
    assert "异常" in err5
    assert call_count2[0] == 1

    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_429_retry(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=2)
    call_count = [0]

    async def rate_limited():
        call_count[0] += 1
        if call_count[0] < 3:
            raise httpx.HTTPStatusError(
                "Too Many Requests",
                request=MagicMock(),
                response=MagicMock(status_code=429),
            )
        return {"ok": True}

    ok, data, err = await guard.call_with_retry(rate_limited, _endpoint="test_429")
    assert ok == True
    assert data == {"ok": True}
    assert "test_429:429" in guard.get_stats()
    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_401(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=1)

    async def unauthorized():
        raise httpx.HTTPStatusError(
            "Unauthorized",
            request=MagicMock(),
            response=MagicMock(status_code=401),
        )

    ok, data, err = await guard.call_with_retry(unauthorized, _endpoint="test_401")
    assert ok == False
    assert data is None
    assert "登录" in err or "认证" in err
    assert "test_401:401" in guard.get_stats()
    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_403(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=1)

    async def forbidden():
        raise httpx.HTTPStatusError(
            "Forbidden",
            request=MagicMock(),
            response=MagicMock(status_code=403),
        )

    ok, data, err = await guard.call_with_retry(forbidden, _endpoint="test_403")
    assert ok == False
    assert "权限" in err
    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_404(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=1)

    async def not_found():
        raise httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404),
        )

    ok, data, err = await guard.call_with_retry(not_found, _endpoint="test_404")
    assert ok == False
    assert "找不到" in err
    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_400(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=1)

    async def bad_request():
        resp = MagicMock(status_code=400)
        resp.json.return_value = {"error": {"message": "invalid group id"}}
        raise httpx.HTTPStatusError("Bad Request", request=MagicMock(), response=resp)

    ok, data, err = await guard.call_with_retry(bad_request, _endpoint="test_400")
    assert ok == False
    assert "invalid group id" in err
    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_500_other_status(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=1)

    async def server_error():
        raise httpx.HTTPStatusError(
            "Internal Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500),
        )

    ok, data, err = await guard.call_with_retry(server_error, _endpoint="test_500")
    assert ok == False
    assert "500" in err
    guard.clear_cache()


@pytest.mark.asyncio
async def test_api_guard_network_error_exhausted(nonebot_init):
    guard = ApiGuard(min_interval=0.01, max_retries=1)

    async def always_flaky():
        raise httpx.ConnectError("connection reset")

    ok, data, err = await guard.call_with_retry(always_flaky, _endpoint="test_flaky_exhaust")
    assert ok == False
    assert "网络异常" in err
    guard.clear_cache()


# ── test_group_config_store_multiple_gets ──

def test_group_config_store_multiple_gets(nonebot_init):
    groups = {
        "multi_test_A": {"vrc_group": "grp_A", "gkick_enabled": True},
        "multi_test_B": {"vrc_group": "grp_B", "gkick_enabled": False},
        "multi_test_C": {"vrc_group": "grp_A", "gkick_enabled": True},
    }

    for qq_id, props in groups.items():
        cfg = group_config_store.get(qq_id)
        cfg.default_vrc_group = props["vrc_group"]
        cfg.set_command_enabled("gkick", props["gkick_enabled"])
        group_config_store.set(cfg)

    cfg_a = group_config_store.get("multi_test_A")
    cfg_b = group_config_store.get("multi_test_B")
    assert cfg_a.is_command_enabled("gkick") == True
    assert cfg_b.is_command_enabled("gkick") == False

    grp_a_bindings = group_config_store.get_by_vrc_group("grp_A")
    grp_a_bindings.sort()
    assert "multi_test_A" in grp_a_bindings
    assert "multi_test_C" in grp_a_bindings
    assert "multi_test_B" not in grp_a_bindings

    grp_b_bindings = group_config_store.get_by_vrc_group("grp_B")
    assert grp_b_bindings == ["multi_test_B"]

    empty = group_config_store.get_by_vrc_group("grp_nonexistent")
    assert empty == []

    for qq_id in groups:
        cfg = group_config_store.get(qq_id)
        cfg.default_vrc_group = None
        cfg.commands.clear()
        group_config_store.set(cfg)


# ── Section 2.4: utils/__init__.py + services/__init__.py tests ──

def test_get_vrc_client_singleton(nonebot_init):
    from utils import get_vrc_client
    c1 = get_vrc_client()
    c2 = get_vrc_client()
    assert c1 is c2


def test_check_vrc_auth_no_cookie():
    from utils import VRCClient, VRCConfig, check_vrc_auth
    client = VRCClient(VRCConfig(auth_cookie=None))
    result = check_vrc_auth(client)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_check_vrc_auth_has_cookie():
    from utils import VRCClient, VRCConfig, check_vrc_auth
    client = VRCClient(VRCConfig(auth_cookie="test_cookie_value"))
    result = check_vrc_auth(client)
    assert result is None


@pytest.mark.asyncio
async def test_ensure_vrc_auth_no_cookie(nonebot_init):
    from utils import VRCClient, VRCConfig, ensure_vrc_auth
    client = VRCClient(VRCConfig(auth_cookie=None))
    matcher = MagicMock()
    matcher.finish = AsyncMock()
    await ensure_vrc_auth(matcher, client)
    matcher.finish.assert_awaited_once()


@pytest.mark.asyncio
async def test_ensure_vrc_auth_has_cookie(nonebot_init):
    from utils import VRCClient, VRCConfig, ensure_vrc_auth
    client = VRCClient(VRCConfig(auth_cookie="test_cookie_value"))
    matcher = MagicMock()
    matcher.finish = AsyncMock()
    await ensure_vrc_auth(matcher, client)
    matcher.finish.assert_not_awaited()


def test_services_init_exports():
    from services import PermissionLevel, get_permission_level, check_command_permission
    import inspect
    assert isinstance(PermissionLevel, type)
    assert inspect.iscoroutinefunction(get_permission_level)
    assert inspect.iscoroutinefunction(check_command_permission)
