"""
配置热重载服务
监控 config 目录下的 YAML 文件变化，通知已注册的观察者进行热重载
"""
import asyncio
from pathlib import Path
from typing import Callable, Awaitable

from nonebot import logger

CONFIG_DIR = Path(__file__).parent.parent / "config"
_DEBOUNCE_SECONDS = 1.0
_DEFAULT_POLL_INTERVAL = 5.0

Observer = Callable[[int], Awaitable[None]]


class ConfigReloadService:
    """配置文件热重载服务"""

    def __init__(self, poll_interval: float = _DEFAULT_POLL_INTERVAL):
        self._poll_interval = poll_interval
        self._observers: list[Observer] = []
        self._file_mtimes: dict[Path, float] = {}
        self._reload_lock = asyncio.Lock()
        self._generation = 0
        self._watcher_task: asyncio.Task | None = None
        self._init_mtimes()

    def _init_mtimes(self):
        for yml_file in CONFIG_DIR.glob("*.yml"):
            try:
                self._file_mtimes[yml_file] = yml_file.stat().st_mtime
            except OSError:
                pass
        for yaml_file in CONFIG_DIR.glob("*.yaml"):
            try:
                self._file_mtimes[yaml_file] = yaml_file.stat().st_mtime
            except OSError:
                pass

    def _has_changes(self) -> bool:
        all_files = set()
        all_files.update(CONFIG_DIR.glob("*.yml"))
        all_files.update(CONFIG_DIR.glob("*.yaml"))
        changed = False
        for file_path in all_files:
            try:
                current_mtime = file_path.stat().st_mtime
            except OSError:
                continue
            if current_mtime != self._file_mtimes.get(file_path, 0):
                changed = True
            self._file_mtimes[file_path] = current_mtime
        return changed

    async def _watch_loop(self):
        while True:
            try:
                if self._has_changes():
                    logger.info("检测到配置文件变化，等待 %.1f 秒去抖后触发热重载", _DEBOUNCE_SECONDS)
                    await asyncio.sleep(_DEBOUNCE_SECONDS)
                    self._has_changes()
                    await self._notify_all()
                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                logger.info("配置文件监控已停止")
                return
            except Exception as e:
                logger.error(f"配置文件监控异常: {e}")
                await asyncio.sleep(self._poll_interval)

    async def _notify_all(self):
        async with self._reload_lock:
            self._generation += 1
            gen = self._generation
            logger.info(f"开始热重载配置 generation={gen}, {len(self._observers)} 个观察者")
            for observer in self._observers:
                try:
                    await observer(gen)
                except Exception as e:
                    logger.error(f"观察者 {observer!r} 执行失败: {e}")

    @property
    def generation(self) -> int:
        return self._generation

    def subscribe(self, callback: Observer, first: bool = False):
        if callback not in self._observers:
            if first:
                self._observers.insert(0, callback)
            else:
                self._observers.append(callback)

    def unsubscribe(self, callback: Observer):
        try:
            self._observers.remove(callback)
        except ValueError:
            pass

    def start_watching(self):
        if self._watcher_task is None or self._watcher_task.done():
            self._init_mtimes()
            self._watcher_task = asyncio.ensure_future(self._watch_loop())
            logger.info("配置文件热重载监控已启动")

    def stop_watching(self):
        if self._watcher_task and not self._watcher_task.done():
            self._watcher_task.cancel()
            self._watcher_task = None

    async def trigger_reload(self):
        await self._notify_all()


config_reload_service = ConfigReloadService()
