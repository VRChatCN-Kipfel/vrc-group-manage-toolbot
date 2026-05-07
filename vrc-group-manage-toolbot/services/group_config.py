import json
from typing import Optional

from pydantic import BaseModel
from nonebot_plugin_localstore import get_data_dir


class GroupConfig(BaseModel):
    qq_group_id: str
    default_vrc_group: Optional[str] = None
    notify_enabled: bool = False
    admin_ops_enabled: bool = True
    allow_user_bind: bool = True


class GroupConfigStore:
    def __init__(self):
        self._file = get_data_dir("vrc_toolbot") / "group_configs.json"
        self._configs: dict[str, GroupConfig] = {}
        self._load()

    def _load(self):
        if self._file.exists():
            data = json.loads(self._file.read_text(encoding="utf-8"))
            self._configs = {
                k: GroupConfig(**v) for k, v in data.items()
            }

    def _save(self):
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.model_dump() for k, v in self._configs.items()}
        self._file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get(self, qq_group_id: str) -> GroupConfig:
        key = str(qq_group_id)
        if key not in self._configs:
            self._configs[key] = GroupConfig(qq_group_id=key)
        return self._configs[key]

    def set(self, config: GroupConfig):
        self._configs[config.qq_group_id] = config
        self._save()


group_config_store = GroupConfigStore()
