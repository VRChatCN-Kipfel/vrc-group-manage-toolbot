"""
API 守卫服务测试 - 实测试

测试 API 限流、重试、缓存等功能
"""
import asyncio
from typing import Optional
import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch
from nonebug import App
from tests import create_mock_bot


class TestApiGuardReal:
    """API 守卫实测试"""
    
    @pytest.mark.asyncio
    async def test_api_guard_initialization(self, app: App):
        """
        实测试：API 守卫初始化
        
        验证 ApiGuard 可以正确创建
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建 API 守卫
        guard = ApiGuard(min_interval=1.0, max_retries=2)
        
        assert guard.min_interval == 1.0
        assert guard.max_retries == 2
        assert guard._last_request_time == 0
        assert len(guard._cache) == 0
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, app: App):
        """
        实测试：缓存操作
        
        验证缓存的读写和过期机制
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        
        guard = ApiGuard()
        
        # 设置缓存
        guard.cache_set("test_key", "test_value", ttl=60)
        
        # 读取缓存
        cached = guard.cache_get("test_key")
        assert cached == "test_value"
        
        # 读取不存在的缓存
        not_exists = guard.cache_get("nonexistent")
        assert not_exists is None
        
        # 清除缓存
        guard.clear_cache()
        cleared = guard.cache_get("test_key")
        assert cleared is None
    
    @pytest.mark.asyncio
    async def test_cache_expiry(self, app: App):
        """
        实测试：缓存过期
        
        验证缓存会在 TTL 后过期
        """
        from services.api_guard import ApiGuard
        import time
        
        bot, ctx = await create_mock_bot(app)
        
        guard = ApiGuard()
        
        # 设置一个立即过期的缓存
        guard.cache_set("expire_key", "value", ttl=0)
        
        # 等待一小段时间
        await asyncio.sleep(0.1)
        
        # 应该已经过期
        expired = guard.cache_get("expire_key")
        assert expired is None
    
    @pytest.mark.asyncio
    async def test_stats_tracking(self, app: App):
        """
        实测试：统计追踪
        
        验证 API 调用统计功能
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        
        guard = ApiGuard()
        
        # 初始统计应该为空
        stats = guard.get_stats()
        assert isinstance(stats, dict)
        
        # 手动添加一些统计
        guard._stats["test_endpoint:ok"] += 1
        guard._stats["test_endpoint:429"] += 2
        
        stats = guard.get_stats()
        assert stats["test_endpoint:ok"] == 1
        assert stats["test_endpoint:429"] == 2
    
    @pytest.mark.asyncio
    async def test_wait_if_needed(self, app: App):
        """
        实测试：请求间隔控制
        
        验证 API 请求间隔限制
        """
        from services.api_guard import ApiGuard
        import time
        
        bot, ctx = await create_mock_bot(app)
        
        guard = ApiGuard(min_interval=0.1)
        
        # 第一次调用应该立即返回
        start = time.time()
        await guard.wait_if_needed()
        elapsed1 = time.time() - start
        
        # 第二次调用应该等待
        start = time.time()
        await guard.wait_if_needed()
        elapsed2 = time.time() - start
        
        # 第二次应该有一定的等待时间
        assert elapsed2 >= 0.05  # 允许一定的误差
    
    @pytest.mark.asyncio
    async def test_call_with_retry_success(self, app: App):
        """
        实测试：API 调用成功
        
        验证成功的 API 调用
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        
        guard = ApiGuard()
        
        # 模拟成功的 API 调用
        async def mock_api():
            return {"success": True}
        
        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test"
        )
        
        assert success is True
        assert result == {"success": True}
        assert error is None
    
    @pytest.mark.asyncio
    async def test_call_with_retry_exception(self, app: App):
        """
        实测试：API 调用异常处理
        
        验证异常情况的处理
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        
        guard = ApiGuard(max_retries=1)
        
        # 模拟失败的 API 调用
        async def mock_api_fail():
            raise Exception("Test error")
        
        success, result, error = await guard.call_with_retry(
            mock_api_fail, _endpoint="test_fail"
        )
        
        assert success is False
        assert result is None
        assert error is not None
        assert "Test error" in error
    
    @pytest.mark.asyncio
    async def test_global_api_guard_instance(self, app: App):
        """
        实测试：全局 API 守卫实例
        
        验证全局 api_guard 实例存在且可用
        """
        from services.api_guard import api_guard, ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证是 ApiGuard 实例
        assert isinstance(api_guard, ApiGuard)
        
        # 验证可以使用
        stats = api_guard.get_stats()
        assert isinstance(stats, dict)


def _make_http_error(status: int, json_body: Optional[dict] = None):
    resp = Mock()
    resp.status_code = status
    resp.json.return_value = json_body or {}
    return httpx.HTTPStatusError(f"{status} error", request=Mock(), response=resp)


class TestApiGuardHttpErrors:
    @pytest.mark.asyncio
    async def test_call_with_429_retry(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=2)

        async def mock_api():
            raise _make_http_error(429)

        with patch("asyncio.sleep", AsyncMock()):
            success, result, error = await guard.call_with_retry(
                mock_api, _endpoint="test_429"
            )

        assert success is False
        assert result is None
        assert "VRChat服务器繁忙" in error

    @pytest.mark.asyncio
    async def test_call_with_429_retry_success(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=2)
        call_count = [0]

        async def mock_api():
            call_count[0] += 1
            if call_count[0] < 2:
                raise _make_http_error(429)
            return {"ok": True}

        with patch("asyncio.sleep", AsyncMock()):
            success, result, error = await guard.call_with_retry(
                mock_api, _endpoint="test_429"
            )

        assert success is True
        assert result == {"ok": True}
        assert error is None
        assert call_count[0] >= 2

    @pytest.mark.asyncio
    async def test_call_with_401(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=0)

        async def mock_api():
            raise _make_http_error(401)

        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test_401"
        )

        assert success is False
        assert result is None
        assert "尚未登录" in error

    @pytest.mark.asyncio
    async def test_call_with_403(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=0)

        async def mock_api():
            raise _make_http_error(403)

        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test_403"
        )

        assert success is False
        assert result is None
        assert "权限" in error

    @pytest.mark.asyncio
    async def test_call_with_404(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=0)

        async def mock_api():
            raise _make_http_error(404)

        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test_404"
        )

        assert success is False
        assert result is None
        assert "找不到" in error

    @pytest.mark.asyncio
    async def test_call_with_400(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=0)

        async def mock_api():
            raise _make_http_error(400, {"error": {"message": "groupId is required"}})

        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test_400"
        )

        assert success is False
        assert result is None
        assert "参数不正确" in error
        assert "groupId is required" in error

    @pytest.mark.asyncio
    async def test_call_with_400_no_detail(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=0)

        async def mock_api():
            raise _make_http_error(400)

        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test_400"
        )

        assert success is False
        assert result is None
        assert error == "参数不正确"

    @pytest.mark.asyncio
    async def test_call_with_500(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=0)

        async def mock_api():
            raise _make_http_error(500)

        success, result, error = await guard.call_with_retry(
            mock_api, _endpoint="test_500"
        )

        assert success is False
        assert result is None
        assert "API错误" in error
        assert "500" in error

    @pytest.mark.asyncio
    async def test_call_with_network_error_exhausted(self, app: App):
        from services.api_guard import ApiGuard

        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(min_interval=0, max_retries=2)

        async def mock_api():
            raise httpx.RequestError("Connection timeout")

        with patch("asyncio.sleep", AsyncMock()):
            success, result, error = await guard.call_with_retry(
                mock_api, _endpoint="test_network"
            )

        assert success is False
        assert result is None
        assert "网络异常" in error
