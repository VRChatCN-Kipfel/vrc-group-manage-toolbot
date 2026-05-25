"""
Unit tests for ConfigReloadService
"""
import asyncio
from unittest.mock import patch, MagicMock

import pytest

from services.config_reload import ConfigReloadService, CONFIG_DIR, _DEBOUNCE_SECONDS


class TestConfigReloadService:
    """UT-1: ConfigReloadService 单元测试"""

    def test_construction_generation_zero(self):
        """UT-1.1: 构造后 generation=0"""
        svc = ConfigReloadService()
        assert svc.generation == 0

    def test_construction_has_observers_empty(self):
        """构造后 _observers 为空且 _reload_lock 就绪"""
        svc = ConfigReloadService()
        assert svc._observers == []
        assert svc._reload_lock is not None

    async def test_subscribe_adds_observer(self):
        """UT-1.2: subscribe 注册回调"""
        svc = ConfigReloadService()

        async def cb(gen: int):
            pass

        svc.subscribe(cb)
        assert len(svc._observers) == 1
        assert svc._observers[0] is cb

    async def test_subscribe_dedup(self):
        """UT-1.3: subscribe 重复注册去重"""
        svc = ConfigReloadService()

        async def cb(gen: int):
            pass

        svc.subscribe(cb)
        svc.subscribe(cb)
        assert len(svc._observers) == 1

    async def test_unsubscribe_removes_observer(self):
        """UT-1.4: unsubscribe 移除回调"""
        svc = ConfigReloadService()

        async def cb(gen: int):
            pass

        svc.subscribe(cb)
        svc.unsubscribe(cb)
        assert len(svc._observers) == 0

    async def test_unsubscribe_nonexistent_no_error(self):
        """UT-1.5: unsubscribe 不存在的回调不抛异常"""
        svc = ConfigReloadService()

        async def cb(gen: int):
            pass

        try:
            svc.unsubscribe(cb)
        except Exception as e:
            pytest.fail(f"unsubscribe 不应抛异常: {e}")

    async def test_trigger_reload_increments_generation(self):
        """UT-1.6: trigger_reload 递增 generation 并通知观察者"""
        svc = ConfigReloadService()
        received_gen = []

        async def cb(gen: int):
            received_gen.append(gen)

        svc.subscribe(cb)
        await svc.trigger_reload()
        assert svc.generation == 1
        assert received_gen == [1]

        await svc.trigger_reload()
        assert svc.generation == 2
        assert received_gen == [1, 2]

    async def test_multiple_observers_notified_in_order(self):
        """UT-1.7: 多个观察者按注册顺序调用"""
        svc = ConfigReloadService()
        call_order = []

        async def cb1(gen: int):
            call_order.append(1)

        async def cb2(gen: int):
            call_order.append(2)

        async def cb3(gen: int):
            call_order.append(3)

        svc.subscribe(cb1)
        svc.subscribe(cb2)
        svc.subscribe(cb3)
        await svc.trigger_reload()
        assert call_order == [1, 2, 3]

    async def test_subscribe_first_inserts_at_head(self):
        """UT-1.7b: subscribe(first=True) 插在列表头部"""
        svc = ConfigReloadService()
        call_order = []

        async def cb1(gen: int):
            call_order.append(1)

        async def cb2(gen: int):
            call_order.append(2)

        svc.subscribe(cb1)
        svc.subscribe(cb2, first=True)
        await svc.trigger_reload()
        assert call_order == [2, 1]

    async def test_one_observer_failure_does_not_block_others(self):
        """UT-1.8: 单个观察者异常不阻断其他观察者"""
        svc = ConfigReloadService()
        called = []

        async def failing_cb(gen: int):
            called.append("fail")
            raise RuntimeError("test error")

        async def normal_cb(gen: int):
            called.append("normal")

        svc.subscribe(failing_cb)
        svc.subscribe(normal_cb)
        await svc.trigger_reload()
        assert called == ["fail", "normal"]

    async def test_reload_lock_serializes_concurrent_triggers(self):
        """UT-1.9: _reload_lock 串行化并发 trigger_reload"""
        svc = ConfigReloadService()
        call_order = []
        in_progress = 0
        max_concurrent = 0

        async def cb(gen: int):
            nonlocal in_progress, max_concurrent
            in_progress += 1
            max_concurrent = max(max_concurrent, in_progress)
            call_order.append(gen)
            in_progress -= 1

        svc.subscribe(cb)
        await asyncio.gather(
            svc.trigger_reload(),
            svc.trigger_reload(),
            svc.trigger_reload(),
        )
        assert max_concurrent == 1
        assert len(call_order) == 3
        assert svc.generation == 3

    async def test_start_watching_creates_task(self):
        """start_watching 创建监控 task"""
        svc = ConfigReloadService()
        svc.start_watching()
        assert svc._watcher_task is not None
        assert not svc._watcher_task.done()
        svc.stop_watching()
        await asyncio.sleep(0.1)
        assert svc._watcher_task is None or svc._watcher_task.done()

    async def test_stop_watching_cancels_task(self):
        """stop_watching 取消监控 task"""
        svc = ConfigReloadService()
        svc.start_watching()
        assert svc._watcher_task is not None
        svc.stop_watching()
        await asyncio.sleep(0.1)
        assert svc._watcher_task is None or svc._watcher_task.done()

    async def test_has_changes_new_file_detected(self, temp_config_dir):
        """UT-1.10: _has_changes 检测文件 mtime 变化"""
        with patch("services.config_reload.CONFIG_DIR", temp_config_dir):
            svc = ConfigReloadService()
            assert not svc._has_changes()

            yml_file = temp_config_dir / "test_config.yml"
            yml_file.write_text("key: value", encoding="utf-8")
            assert svc._has_changes()
            assert not svc._has_changes()

    async def test_has_changes_empty_dir_no_error(self, temp_config_dir):
        """UT-1.11: 目录无 yml 文件时不崩溃"""
        with patch("services.config_reload.CONFIG_DIR", temp_config_dir):
            svc = ConfigReloadService()
            try:
                svc._has_changes()
            except Exception as e:
                pytest.fail(f"_has_changes 不应在空目录崩溃: {e}")
