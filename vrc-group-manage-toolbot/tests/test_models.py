import pytest

from pydantic import ValidationError


# ── test_vrc_pydantic_models ──

def test_vrc_pydantic_models(nonebot_init):
    from utils.VRC.vrc_models import (
        User, Instance, Group, GroupMember,
        GroupRole, Announcement, JoinRequest, AuditLogEntry,
    )

    u = User(id="usr_test", displayName="测试用户", username="testuser", status="offline")
    assert u.id == "usr_test"

    g = Group(id="grp_test123", name="测试群组", shortCode="TEST", memberCount=42)
    assert g.id == "grp_test123"

    gm = GroupMember(id="mem_001", groupId="grp_test123", userId="usr_test", roleIds=["role_01"], isRepresenting=False)
    assert gm.userId == "usr_test"

    gr = GroupRole(id="role_01", name="管理员", isManagement=True)
    assert gr.id == "role_01"

    a = Announcement(id="ann_001", title="公告标题", text="公告内容")
    assert a.id == "ann_001"

    jr = JoinRequest(userId="usr_new")
    assert jr.userId == "usr_new"

    ale = AuditLogEntry(
        id="log_001", description="用户加入群组",
        actorId="usr_admin", targetId="usr_new"
    )
    assert ale.id == "log_001"

    inst = Instance(
        id="wrld_test:12345",
        worldId="wrld_test",
        location="wrld_test:12345",
        userCount=8,
        capacity=32,
    )
    assert inst.id == "wrld_test:12345"


# ── test_vrc_config_from_env ──

def test_vrc_config_from_env(nonebot_init):
    from utils.VRC.vrc_config import VRCConfig

    cfg = VRCConfig.from_env()
    assert cfg.base_url == "https://api.vrchat.cloud/api/1"
    assert isinstance(cfg.timeout, int) and cfg.timeout > 0
    assert isinstance(cfg.request_delay, int) and cfg.request_delay > 0

    c2 = VRCConfig()
    assert c2.base_url == "https://api.vrchat.cloud/api/1"
    assert c2.timeout == 30
    assert c2.request_delay == 1000
    assert c2.username is None

    c3 = VRCConfig(username="testuser", password="testpass", timeout=60)
    assert c3.username == "testuser"
    assert c3.timeout == 60


# ── test_pydantic_models_validation ──

def test_pydantic_models_validation(nonebot_init):
    from utils.VRC.vrc_models import (
        User, Group, GroupMember, GroupRole,
        Announcement, JoinRequest, AuditLogEntry, Instance
    )

    with pytest.raises(Exception):
        User()

    u = User(id="u1", displayName="test", extra_field="should_be_ok")
    assert u.id == "u1"

    gm = GroupMember(id="m1", groupId="g1", userId="u1")
    assert gm.roleIds == []
    assert gm.isRepresenting == False

    gr = GroupRole(id="r1", name="Member")
    assert gr.selfAssignable == False
    assert gr.isManagement == False
    assert gr.permissions == []

    inst = Instance(instanceId="inst1", memberCount=10)
    assert inst.id == "inst1"
    assert inst.userCount == 10

    inst2 = Instance(instanceId="i2", world={"id": "wrld_abc", "name": "Test World", "capacity": 32})
    assert inst2.worldId == "wrld_abc"
    assert inst2.worldName == "Test World"
    assert inst2.capacity == 32

    inst3 = Instance(instanceId="i3", location={"location": "wrld_x:12345"}, world="wrld_x")
    assert inst3.location == "wrld_x:12345"

    inst4 = Instance(instanceId="i4", n_users=5, world="wrld_x")
    assert inst4.n_users is None

    jr = JoinRequest(userId="u1")
    assert jr.userId == "u1"
    assert jr.created_at is None


# ── test_command_config_pydantic ──

def test_command_config_pydantic(nonebot_init):
    from services.group_config import CommandConfig
    from services.permission import PermissionLevel

    cc = CommandConfig()
    assert cc.enabled == True
    assert cc.permission == 0
    assert cc.get_permission_level() == PermissionLevel.UNBOUND_USER


@pytest.mark.parametrize("v", [0, 1, 2, 3, 4, 5])
def test_command_config_valid_range(v):
    from services.group_config import CommandConfig
    cc = CommandConfig(permission=v)
    assert cc.permission == v


@pytest.mark.parametrize("v", [-1, 6, 100])
def test_command_config_invalid_range(v):
    from services.group_config import CommandConfig
    with pytest.raises(ValidationError):
        CommandConfig(permission=v)


def test_command_config_bool_parsing():
    from services.group_config import CommandConfig
    cc2a = CommandConfig(enabled="true")
    assert cc2a.enabled == True
    cc2b = CommandConfig(enabled="false")
    assert cc2b.enabled == False
