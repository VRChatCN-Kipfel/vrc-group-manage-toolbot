import json
import time
from typing import Optional

from pydantic import BaseModel
from nonebot_plugin_localstore import get_data_dir


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
            data = json.loads(self._file.read_text(encoding="utf-8"))
            self._bindings = {
                k: BindingRecord(**v) for k, v in data.items()
            }

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


user_binding_store = UserBindingStore()
