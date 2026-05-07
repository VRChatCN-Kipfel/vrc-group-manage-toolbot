import asyncio
import time
from typing import Optional, Any
from collections import defaultdict

import httpx
from nonebot import logger


class ApiGuard:
    def __init__(self, min_interval: float = 1.5, max_retries: int = 3):
        self.min_interval = min_interval
        self.max_retries = max_retries
        self._last_request_time: float = 0
        self._cache: dict[str, tuple[Any, float]] = {}
        self._stats: dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def wait_if_needed(self):
        async with self._lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self._last_request_time = time.time()

    def cache_get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            del self._cache[key]
        return None

    def cache_set(self, key: str, value: Any, ttl: int = 60):
        self._cache[key] = (value, time.time() + float(ttl))

    async def call_with_retry(self, api_call, *args, **kwargs):
        endpoint = kwargs.pop("_endpoint", "unknown")
        cache_key = kwargs.pop("_cache_key", None)
        cache_ttl = kwargs.pop("_cache_ttl", 60)

        if cache_key:
            cached = self.cache_get(cache_key)
            if cached is not None:
                self._stats[f"{endpoint}:cache_hit"] += 1
                return True, cached, None

        for attempt in range(self.max_retries + 1):
            await self.wait_if_needed()

            try:
                result = await api_call(*args, **kwargs)
                self._stats[f"{endpoint}:ok"] += 1
                if cache_key:
                    self.cache_set(cache_key, result, cache_ttl)
                return True, result, None

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                if status == 429:
                    self._stats[f"{endpoint}:429"] += 1
                    if attempt < self.max_retries:
                        wait = (2 ** attempt) * 2
                        logger.warning(
                            f"Rate limited ({endpoint}), retrying in {wait}s "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait)
                        continue
                    return False, None, "VRChat服务器繁忙（已多次重试失败），请稍后再试"

                elif status == 401:
                    self._stats[f"{endpoint}:401"] += 1
                    return False, None, "尚未登录或认证已过期\n请使用 #vrclLogin 或 #vrclLogin cookie=xxx"

                elif status == 403:
                    self._stats[f"{endpoint}:403"] += 1
                    return False, None, "您没有执行此操作的权限"

                elif status == 404:
                    self._stats[f"{endpoint}:404"] += 1
                    return False, None, "找不到指定的资源（ID可能不对）"

                elif status == 400:
                    self._stats[f"{endpoint}:400"] += 1
                    try:
                        detail = e.response.json().get("error", {}).get("message", "")
                    except Exception:
                        detail = ""
                    return False, None, f"参数不正确: {detail}" if detail else "参数不正确"

                else:
                    self._stats[f"{endpoint}:{status}"] += 1
                    return False, None, f"API错误 ({status})"

            except httpx.RequestError as e:
                self._stats[f"{endpoint}:network_error"] += 1
                logger.error(f"API网络异常 ({endpoint}): {e}")
                if attempt < self.max_retries:
                    wait = 2
                    await asyncio.sleep(wait)
                    continue
                return False, None, "网络异常，请稍后再试"

            except Exception as e:
                self._stats[f"{endpoint}:error"] += 1
                logger.error(f"API调用异常 ({endpoint}): {e}")
                return False, None, f"服务异常: {str(e)[:100]}"

        return False, None, "多次重试后仍然失败"

    def get_stats(self) -> dict:
        return dict(self._stats)

    def clear_cache(self):
        self._cache.clear()


api_guard = ApiGuard()
