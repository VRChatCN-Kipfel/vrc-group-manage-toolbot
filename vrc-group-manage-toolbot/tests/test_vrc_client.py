from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import httpx

from utils.VRC.vrc_config import VRCConfig
from utils.VRC.vrc_client import VRCClient


@pytest.fixture
def vrc_client_with_cookie():
    return VRCClient(VRCConfig(auth_cookie="mock_auth_cookie_12345", base_url="https://mock.vrchat/api/1"))


@pytest.fixture
def vrc_client_without_cookie():
    return VRCClient(VRCConfig(auth_cookie=None, base_url="https://mock.vrchat/api/1"))


@pytest.mark.asyncio
async def test_get_current_user(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = {"id": "usr_x", "displayName": "test_user", "username": "testuser"}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_current_user()

    assert result is not None
    assert result.id == "usr_x"
    assert result.displayName == "test_user"
    mock_req.assert_called_once_with("GET", "/auth/user")


@pytest.mark.asyncio
async def test_get_current_user_401(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=MagicMock(status_code=401)
        )
        result = await client.get_current_user()

    assert result is None


@pytest.mark.asyncio
async def test_get_group(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = {"id": "grp_abc", "name": "Test Group", "shortCode": "TEST", "memberCount": 100}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_group("grp_abc")

    assert result is not None
    assert result.id == "grp_abc"
    assert result.name == "Test Group"
    assert result.memberCount == 100
    mock_req.assert_called_once_with("GET", "/groups/grp_abc")


@pytest.mark.asyncio
async def test_get_group_404(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        result = await client.get_group("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_get_group_member(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = {
        "id": "gmem_1",
        "groupId": "grp_abc",
        "userId": "usr_x",
        "roleIds": ["role_01"],
        "isRepresenting": False,
    }

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_group_member("grp_abc", "usr_x")

    assert result is not None
    assert result.id == "gmem_1"
    assert result.groupId == "grp_abc"
    assert result.userId == "usr_x"
    assert result.roleIds == ["role_01"]
    mock_req.assert_called_once_with("GET", "/groups/grp_abc/members/usr_x")


@pytest.mark.asyncio
async def test_get_group_roles(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = [
        {"id": "role_1", "name": "Owner", "isManagement": True},
        {"id": "role_2", "name": "Moderator", "isManagement": True},
        {"id": "role_3", "name": "Member", "isManagement": False},
    ]

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_group_roles("grp_abc")

    assert len(result) == 3
    assert result[0].id == "role_1"
    assert result[0].name == "Owner"
    assert result[1].name == "Moderator"
    assert result[2].name == "Member"
    mock_req.assert_called_once_with("GET", "/groups/grp_abc/roles")


@pytest.mark.asyncio
async def test_get_group_instances(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = [
        {"instanceId": "wrld_test:12345", "worldId": "wrld_test", "userCount": 5},
        {"instanceId": "wrld_test:67890", "worldId": "wrld_test", "userCount": 12},
    ]

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_group_instances("grp_abc")

    assert len(result) == 2
    assert result[0].id == "wrld_test:12345"
    assert result[0].worldId == "wrld_test"
    assert result[1].id == "wrld_test:67890"
    mock_req.assert_called_once_with("GET", "/groups/grp_abc/instances", params={"offset": 0, "n": 50})


@pytest.mark.asyncio
async def test_auth_cookie_missing(vrc_client_without_cookie):
    import os
    from pathlib import Path

    cookie_file = Path("data/auth_cookie.txt")
    original_exists = cookie_file.exists()

    if cookie_file.exists():
        cookie_file.rename(Path("data/auth_cookie.txt.bak"))

    try:
        client = vrc_client_without_cookie
        client.config.auth_cookie = None
        hclient = await client._get_client()
        headers = hclient.headers
        assert "Cookie" not in headers or "auth=" not in headers.get("Cookie", "")
    finally:
        if original_exists and not cookie_file.exists():
            Path("data/auth_cookie.txt.bak").rename(cookie_file)
        elif not original_exists and cookie_file.exists():
            cookie_file.unlink()


@pytest.mark.asyncio
async def test_auth_cookie_from_file():
    from pathlib import Path

    cookie_file = Path("data/auth_cookie.txt")
    original_content = cookie_file.read_text() if cookie_file.exists() else None

    try:
        cookie_file.parent.mkdir(parents=True, exist_ok=True)
        cookie_file.write_text("saved_test_cookie_value")

        client = VRCClient(VRCConfig(auth_cookie=None, base_url="https://mock.vrchat/api/1"))
        client._cookie_file = cookie_file
        client._load_cookie()
        assert client.config.auth_cookie == "saved_test_cookie_value"
    finally:
        if original_content is not None:
            cookie_file.write_text(original_content)
        elif cookie_file.exists():
            cookie_file.unlink()


@pytest.mark.asyncio
async def test_get_instance(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = {"instanceId": "wrld_test:12345", "worldId": "wrld_test"}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_instance("wrld_test:12345")

    assert result is not None
    assert result.id == "wrld_test:12345"
    mock_req.assert_called_once_with("GET", "/instances/wrld_test:12345")


@pytest.mark.asyncio
async def test_get_instance_404(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        result = await client.get_instance("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_get_world(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = {"id": "wrld_abc", "name": "Test World"}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_world("wrld_abc")

    assert result is not None
    assert result.id == "wrld_abc"
    assert result.name == "Test World"
    mock_req.assert_called_once_with("GET", "/worlds/wrld_abc")


@pytest.mark.asyncio
async def test_get_world_404(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        result = await client.get_world("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_get_user(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = {"id": "usr_x", "displayName": "Some User"}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_user("usr_x")

    assert result is not None
    assert result.id == "usr_x"
    assert result.displayName == "Some User"
    mock_req.assert_called_once_with("GET", "/users/usr_x")


@pytest.mark.asyncio
async def test_get_user_404(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        result = await client.get_user("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_get_group_members(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_response = [
        {"id": "gmem_1", "groupId": "grp_abc", "userId": "usr_a", "roleIds": []},
        {"id": "gmem_2", "groupId": "grp_abc", "userId": "usr_b", "roleIds": ["role_01"]},
    ]

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_group_members("grp_abc", n=50, offset=0)

    assert len(result) == 2
    assert result[0].userId == "usr_a"
    assert result[1].userId == "usr_b"
    mock_req.assert_called_once_with("GET", "/groups/grp_abc/members", params={"n": 50, "offset": 0})


@pytest.mark.asyncio
async def test_join_instance(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {}
        result = await client.join_instance("wrld_test:12345")

    assert result == True
    mock_req.assert_called_once_with("PUT", "/instances/wrld_test:12345/join")


@pytest.mark.asyncio
async def test_leave_instance(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {}
        result = await client.leave_instance("wrld_test:12345")

    assert result == True
    mock_req.assert_called_once_with("DELETE", "/instances/wrld_test:12345/leave")


@pytest.mark.asyncio
async def test_get_friends(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = [{"id": "usr_f1", "displayName": "Friend1"}]
        result = await client.get_friends()

    assert len(result) == 1
    assert result[0]["displayName"] == "Friend1"
    mock_req.assert_called_once_with("GET", "/auth/user/friends")


@pytest.mark.asyncio
async def test_get_friends_empty(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = "not_a_list"
        result = await client.get_friends()

    assert result == []


@pytest.mark.asyncio
async def test_refresh_auth(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"ok": True}
        result = await client.refresh_auth()

    assert result == True
    assert client.is_authenticated == True


@pytest.mark.asyncio
async def test_refresh_auth_fail(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=MagicMock(status_code=401)
        )
        result = await client.refresh_auth()

    assert result == False
    assert client.is_authenticated == False


@pytest.mark.asyncio
async def test_send_friend_request(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"status": "sent"}
        result = await client.send_friend_request("usr_x")

    assert result == {"status": "sent"}
    mock_req.assert_called_once_with("POST", "/user/usr_x/friendRequest")


@pytest.mark.asyncio
async def test_check_friend_status(vrc_client_with_cookie):
    client = vrc_client_with_cookie

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"isFriend": True}
        result = await client.check_friend_status("usr_x")

    assert result == {"isFriend": True}
    mock_req.assert_called_once_with("GET", "/user/usr_x/friendStatus")


@pytest.mark.asyncio
async def test_close(vrc_client_with_cookie):
    client = vrc_client_with_cookie
    mock_aclose = AsyncMock()
    client.client = MagicMock()
    client.client.aclose = mock_aclose

    await client.close()

    mock_aclose.assert_awaited_once()
    assert client.client is None
    assert client._authenticated == False
