import json
import time
from typing import Optional

from pydantic import BaseModel
from nonebot import logger
from nonebot_plugin_localstore import get_data_dir
from .global_config import global_config
from .scheduler_service import scheduler_service


class BindingRecord(BaseModel):
    qq_id: str
    vrc_user_id: str
    vrc_display_name: str
    bound_at: float
    confirmed: bool = False
    verify_code: Optional[str] = None
    verify_code_expires: Optional[float] = None


class UserBindingStore:
    def __init__(self):
        self._file = get_data_dir("vrc_toolbot") / "bindings.json"
        self._bindings: dict[str, BindingRecord] = {}
        self._load()

    def _load(self):
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text(encoding="utf-8"))
                self._bindings = {
                    k: BindingRecord(**v) for k, v in data.items()
                }
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Failed to load bindings, resetting: {e}")
                self._bindings = {}

    def _save(self):
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.model_dump() for k, v in self._bindings.items()}
        self._file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get_by_qq(self, qq_id: str) -> Optional[BindingRecord]:
        return self._bindings.get(str(qq_id))

    def get_by_vrc(self, vrc_user_id: str) -> Optional[BindingRecord]:
        for binding in self._bindings.values():
            if binding.vrc_user_id == vrc_user_id:
                return binding
        return None

    def set(self, binding: BindingRecord):
        self._bindings[binding.qq_id] = binding
        self._save()

    def remove(self, qq_id: str):
        self._bindings.pop(str(qq_id), None)
        self._save()

    def cleanup_expired(self):
        """清理已过期的未确认绑定记录"""
        if not global_config.is_auto_cleanup_enabled:
            return
        
        now = time.time()
        expired_qqs = []
        for qq_id, binding in self._bindings.items():
            if not binding.confirmed and binding.verify_code_expires and now > binding.verify_code_expires:
                expired_qqs.append(qq_id)
        
        for qq_id in expired_qqs:
            del self._bindings[qq_id]
            logger.info(f"自动清理过期绑定记录: {qq_id}")
        
        if expired_qqs:
            self._save()
            logger.info(f"共清理 {len(expired_qqs)} 条过期绑定记录")


user_binding_store = UserBindingStore()

# --- 自动注册清理任务 ---
def _register_cleanup_task():
    if global_config.is_auto_cleanup_enabled:
        interval = global_config.cleanup_interval
        try:
            scheduler_service.add_interval_task(
                func=user_binding_store.cleanup_expired,
                seconds=interval,
                task_id="cleanup_expired_bindings",
                force_replace=True
            )
            logger.info(f"[UserBinding] 已注册定期清理任务，间隔: {interval}秒")
        except Exception as e:
            logger.error(f"[UserBinding] 注册清理任务失败: {e}")
    else:
        logger.info("[UserBinding] 自动清理功能已在配置中禁用")

_register_cleanup_task()
