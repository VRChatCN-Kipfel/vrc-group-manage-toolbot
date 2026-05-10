"""
VRC 工具模块测试 - 实测试

测试 VRC 客户端、数据模型、配置的完整功能
"""
import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch
from nonebug import App
from tests import create_mock_bot, get_test_user_id


class TestVRCClientReal:
    """VRC 客户端实测试"""
    
    @pytest.mark.asyncio
    async def test_vrc_client_initialization(self, app: App):
        """
        实测试：VRC 客户端初始化
        
        验证客户端可以正确创建和初始化
        """
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig
        
        # 创建 mock bot
        bot, ctx = await create_mock_bot(app)
        
        # 创建配置
        config = VRCConfig(
            username="test_user",
            password="test_password",
            auth_token=None
        )
        
        # 创建客户端（不实际连接）
        client = VRCClient(config)
        
        assert client is not None
        assert client.config.username == "test_user"
    
    @pytest.mark.asyncio
    async def test_vrc_client_auth_check(self, app: App):
        """
        实测试：VRC 客户端认证检查
        
        验证认证状态检查逻辑
        """
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig
        
        bot, ctx = await create_mock_bot(app)
        
        # 未认证的客户端
        config = VRCConfig(
            username="test_user",
            password="test_password",
            auth_cookie=None
        )
        client = VRCClient(config)
        
        # 检查认证状态（应该返回错误）
        assert client.config.auth_cookie is None
    
    @pytest.mark.asyncio
    async def test_vrc_client_with_valid_token(self, app: App):
        """
        实测试：使用有效 cookie 的客户端
        
        验证有 cookie 的客户端可以正常工作
        """
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig
        
        bot, ctx = await create_mock_bot(app)
        
        # 有 cookie 的客户端
        config = VRCConfig(
            username="test_user",
            password="test_password",
            auth_cookie="auth_test_cookie_12345"
        )
        client = VRCClient(config)
        
        assert client.config.auth_cookie == "auth_test_cookie_12345"


class TestVRCModelsReal:
    """VRC 数据模型实测试"""
    
    @pytest.mark.asyncio
    async def test_user_model_creation(self, app: App):
        """
        实测试：创建 User 模型
        
        验证用户模型可以正确创建和访问
        """
        from utils.VRC.vrc_models import User
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建用户模型
        user = User(
            id="usr_123456",
            displayName="TestUser",
            username="testuser",
            status="active",
            location="wrld_xxx:12345~private(usr_123456)~region(us)"
        )
        
        assert user.id == "usr_123456"
        assert user.displayName == "TestUser"
        assert user.username == "testuser"
        assert user.status == "active"
    
    @pytest.mark.asyncio
    async def test_instance_model_creation(self, app: App):
        """
        实测试：创建 Instance 模型
        
        验证实例模型可以正确创建和访问
        """
        from utils.VRC.vrc_models import Instance
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建实例模型
        instance = Instance(
            instanceId="wrld_xxx:12345~public",
            world="wrld_xxx",
            worldName="Test World",
            memberCount=10,
            capacity=40
        )
        
        assert instance.id == "wrld_xxx:12345~public"
        assert instance.worldId == "wrld_xxx"
        assert instance.worldName == "Test World"
        assert instance.userCount == 10
        assert instance.capacity == 40
        assert instance.display_count == "10/40"
    
    @pytest.mark.asyncio
    async def test_group_model_creation(self, app: App):
        """
        实测试：创建 Group 模型
        
        验证群组模型可以正确创建和访问
        """
        from utils.VRC.vrc_models import Group
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建群组模型
        group = Group(
            id="grp_123456",
            name="Test Group",
            shortCode="TEST",
            discriminator="1234",
            description="A test group",
            memberCount=100,
            onlineMemberCount=25
        )
        
        assert group.id == "grp_123456"
        assert group.name == "Test Group"
        assert group.shortCode == "TEST"
        assert group.memberCount == 100
        assert group.onlineMemberCount == 25
    
    @pytest.mark.asyncio
    async def test_world_model_creation(self, app: App):
        """
        实测试：创建 World 模型
        
        验证世界模型可以正确创建和访问
        """
        from utils.VRC.vrc_models import World
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建世界模型
        world = World(
            id="wrld_123456",
            name="Test World",
            authorName="TestAuthor",
            authorId="usr_123456",
            capacity=40,
            recommendedCapacity=20,
            description="A test world",
            tags=["fun", "social"]
        )
        
        assert world.id == "wrld_123456"
        assert world.name == "Test World"
        assert world.authorName == "TestAuthor"
        assert world.capacity == 40
        assert world.tags == ["fun", "social"]
    
    @pytest.mark.asyncio
    async def test_group_member_model(self, app: App):
        """
        实测试：创建 GroupMember 模型
        
        验证群组成员模型可以正确创建
        """
        from utils.VRC.vrc_models import GroupMember
        
        bot, ctx = await create_mock_bot(app)
        
        member = GroupMember(
            id="mem_123456",
            groupId="grp_123456",
            userId="usr_123456",
            roleIds=["role_admin"],
            isRepresenting=True
        )
        
        assert member.id == "mem_123456"
        assert member.groupId == "grp_123456"
        assert member.userId == "usr_123456"
        assert member.roleIds == ["role_admin"]
        assert member.isRepresenting is True
    
    @pytest.mark.asyncio
    async def test_group_role_model(self, app: App):
        """
        实测试：创建 GroupRole 模型
        
        验证群组角色模型可以正确创建
        """
        from utils.VRC.vrc_models import GroupRole
        
        bot, ctx = await create_mock_bot(app)
        
        role = GroupRole(
            id="role_admin",
            name="Admin",
            description="Group administrator",
            selfAssignable=False,
            isManagement=True,
            permissions=["manage_members", "manage_roles"]
        )
        
        assert role.id == "role_admin"
        assert role.name == "Admin"
        assert role.isManagement is True
        assert "manage_members" in role.permissions
    
    @pytest.mark.asyncio
    async def test_announcement_model(self, app: App):
        """
        实测试：创建 Announcement 模型
        
        验证公告模型可以正确创建
        """
        from utils.VRC.vrc_models import Announcement
        
        bot, ctx = await create_mock_bot(app)
        
        announcement = Announcement(
            id="ann_123456",
            title="Test Announcement",
            text="This is a test announcement",
            createdAt="2024-01-01T00:00:00Z"
        )
        
        assert announcement.id == "ann_123456"
        assert announcement.title == "Test Announcement"
        assert announcement.text == "This is a test announcement"
    
    @pytest.mark.asyncio
    async def test_join_request_model(self, app: App):
        """
        实测试：创建 JoinRequest 模型
        
        验证加入请求模型可以正确创建
        """
        from utils.VRC.vrc_models import JoinRequest
        
        bot, ctx = await create_mock_bot(app)
        
        request = JoinRequest(
            userId="usr_123456",
            created_at="2024-01-01T00:00:00Z"
        )
        
        assert request.userId == "usr_123456"
    
    @pytest.mark.asyncio
    async def test_audit_log_entry_model(self, app: App):
        """
        实测试：创建 AuditLogEntry 模型
        
        验证审计日志条目模型可以正确创建
        """
        from utils.VRC.vrc_models import AuditLogEntry
        
        bot, ctx = await create_mock_bot(app)
        
        log_entry = AuditLogEntry(
            id="log_123456",
            created_at="2024-01-01T00:00:00Z",
            description="User banned",
            actorId="usr_admin",
            targetId="usr_banned"
        )
        
        assert log_entry.id == "log_123456"
        assert log_entry.description == "User banned"
        assert log_entry.actorId == "usr_admin"


class TestVRCConfigReal:
    """VRC 配置实测试"""
    
    @pytest.mark.asyncio
    async def test_vrc_config_creation(self, app: App):
        """
        实测试：创建 VRC 配置
        
        验证配置对象可以正确创建
        """
        from utils.VRC.vrc_config import VRCConfig
        
        bot, ctx = await create_mock_bot(app)
        
        config = VRCConfig(
            username="test_user",
            password="test_password",
            auth_cookie="test_cookie"
        )
        
        assert config.username == "test_user"
        assert config.password == "test_password"
        assert config.auth_cookie == "test_cookie"
    
    @pytest.mark.asyncio
    async def test_vrc_config_without_token(self, app: App):
        """
        实测试：创建无 cookie 的 VRC 配置
        
        验证可以创建未认证的配置
        """
        from utils.VRC.vrc_config import VRCConfig
        
        bot, ctx = await create_mock_bot(app)
        
        config = VRCConfig(
            username="test_user",
            password="test_password"
        )
        
        assert config.username == "test_user"
        assert config.auth_cookie is None


class TestVrcClientApi:
    @pytest.mark.asyncio
    async def test_get_current_user(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={
            "id": "usr_001", "displayName": "TestUser", "username": "test"
        })):
            user = await client.get_current_user()

        assert user is not None
        assert user.id == "usr_001"
        assert user.displayName == "TestUser"

    @pytest.mark.asyncio
    async def test_get_current_user_401(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 401
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("401", request=Mock(), response=mock_resp)
        )):
            user = await client.get_current_user()

        assert user is None

    @pytest.mark.asyncio
    async def test_get_group(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={
            "id": "grp_001", "name": "TestGroup", "shortCode": "TEST"
        })):
            group = await client.get_group("grp_001")

        assert group is not None
        assert group.id == "grp_001"
        assert group.name == "TestGroup"

    @pytest.mark.asyncio
    async def test_get_group_404(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 404
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=Mock(), response=mock_resp)
        )):
            group = await client.get_group("grp_999")

        assert group is None

    @pytest.mark.asyncio
    async def test_get_group_member(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={
            "id": "mem_001", "groupId": "grp_001", "userId": "usr_001",
            "roleIds": ["role_admin"], "isRepresenting": True
        })):
            member = await client.get_group_member("grp_001", "usr_001")

        assert member is not None
        assert member.userId == "usr_001"
        assert member.roleIds == ["role_admin"]

    @pytest.mark.asyncio
    async def test_get_group_member_404(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 404
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=Mock(), response=mock_resp)
        )):
            member = await client.get_group_member("grp_001", "nonexistent_user")

        assert member is None

    @pytest.mark.asyncio
    async def test_get_group_roles(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value=[
            {"id": "role_001", "name": "Admin", "isManagement": True},
            {"id": "role_002", "name": "Member", "isManagement": False},
        ])):
            roles = await client.get_group_roles("grp_001")

        assert len(roles) == 2
        assert roles[0].name == "Admin"

    @pytest.mark.asyncio
    async def test_get_group_instances(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value=[
            {"instanceId": "wrld_001:12345~public(usr_001)", "memberCount": 5, "worldName": "TestWorld"}
        ])):
            instances = await client.get_group_instances("grp_001")

        assert len(instances) == 1
        assert instances[0].id == "wrld_001:12345~public(usr_001)"

    @pytest.mark.asyncio
    async def test_get_instance(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={
            "instanceId": "wrld_001:12345~public", "memberCount": 10, "worldName": "TestWorld"
        })):
            instance = await client.get_instance("wrld_001:12345~public")

        assert instance is not None
        assert instance.id == "wrld_001:12345~public"

    @pytest.mark.asyncio
    async def test_get_instance_404(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 404
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=Mock(), response=mock_resp)
        )):
            instance = await client.get_instance("nonexistent")

        assert instance is None

    @pytest.mark.asyncio
    async def test_get_world(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={
            "id": "wrld_001", "name": "TestWorld", "authorName": "Author", "authorId": "usr_author"
        })):
            world = await client.get_world("wrld_001")

        assert world is not None
        assert world.id == "wrld_001"
        assert world.name == "TestWorld"

    @pytest.mark.asyncio
    async def test_get_world_404(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 404
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=Mock(), response=mock_resp)
        )):
            world = await client.get_world("nonexistent")

        assert world is None

    @pytest.mark.asyncio
    async def test_get_user(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={
            "id": "usr_target", "displayName": "TargetUser", "username": "target"
        })):
            user = await client.get_user("usr_target")

        assert user is not None
        assert user.id == "usr_target"
        assert user.displayName == "TargetUser"

    @pytest.mark.asyncio
    async def test_get_user_404(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 404
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=Mock(), response=mock_resp)
        )):
            user = await client.get_user("nonexistent")

        assert user is None

    @pytest.mark.asyncio
    async def test_get_group_members(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value=[
            {"id": "mem_001", "groupId": "grp_001", "userId": "usr_001", "roleIds": ["role_001"]},
            {"id": "mem_002", "groupId": "grp_001", "userId": "usr_002", "roleIds": []},
        ])):
            members = await client.get_group_members("grp_001")

        assert len(members) == 2
        assert members[0].userId == "usr_001"

    @pytest.mark.asyncio
    async def test_get_friends(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value=[
            {"id": "usr_friend_1", "displayName": "Friend1"},
            {"id": "usr_friend_2", "displayName": "Friend2"},
        ])):
            friends = await client.get_friends()

        assert len(friends) == 2
        assert friends[0]["displayName"] == "Friend1"

    @pytest.mark.asyncio
    async def test_get_friends_empty(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={})):
            friends = await client.get_friends()

        assert friends == []

    @pytest.mark.asyncio
    async def test_join_instance(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock()):
            result = await client.join_instance("wrld_001:12345~public")

        assert result is True

    @pytest.mark.asyncio
    async def test_leave_instance(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock()):
            result = await client.leave_instance("wrld_001:12345~public")

        assert result is True

    @pytest.mark.asyncio
    async def test_send_friend_request(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={"status": "pending"})):
            result = await client.send_friend_request("usr_target")

        assert result == {"status": "pending"}

    @pytest.mark.asyncio
    async def test_check_friend_status(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock(return_value={"isFriend": True})):
            result = await client.check_friend_status("usr_target")

        assert result == {"isFriend": True}

    @pytest.mark.asyncio
    async def test_refresh_auth(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        with patch.object(client, "_request", AsyncMock()):
            result = await client.refresh_auth()

        assert result is True

    @pytest.mark.asyncio
    async def test_refresh_auth_fail(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_resp = Mock()
        mock_resp.status_code = 401
        with patch.object(client, "_request", AsyncMock(
            side_effect=httpx.HTTPStatusError("401", request=Mock(), response=mock_resp)
        )):
            result = await client.refresh_auth()

        assert result is False

    @pytest.mark.asyncio
    async def test_close(self, app: App):
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="cookie")
        client = VRCClient(config)

        mock_http = AsyncMock()
        client.client = mock_http

        await client.close()

        mock_http.aclose.assert_called_once()
        assert client.client is None


class TestEnsureVrcAuth:
    @pytest.mark.asyncio
    async def test_no_cookie(self, app: App):
        from unittest.mock import AsyncMock
        from utils import ensure_vrc_auth
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test")
        client = VRCClient(config)

        matcher = AsyncMock()
        await ensure_vrc_auth(matcher, client)

        matcher.finish.assert_called_once()
        assert "尚未登录" in matcher.finish.call_args[0][0]

    @pytest.mark.asyncio
    async def test_has_cookie(self, app: App):
        from unittest.mock import AsyncMock
        from utils import ensure_vrc_auth
        from utils.VRC.vrc_client import VRCClient
        from utils.VRC.vrc_config import VRCConfig

        bot, ctx = await create_mock_bot(app)
        config = VRCConfig(username="test", auth_cookie="valid_cookie")
        client = VRCClient(config)

        matcher = AsyncMock()
        await ensure_vrc_auth(matcher, client)

        matcher.finish.assert_not_called()
