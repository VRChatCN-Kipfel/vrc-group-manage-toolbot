import json
from typing import Optional, Dict

from pydantic import BaseModel, Field
from nonebot import logger
from nonebot_plugin_localstore import get_data_dir
from .permission import PermissionLevel


# 定义所有可用的命令及其默认配置
COMMAND_DEFAULTS = {
    # 系统/认证模块
    "vrclLogin": {"enabled": True, "permission": PermissionLevel.USER},
    "2fa": {"enabled": True, "permission": PermissionLevel.USER},
    "vrcCheck": {"enabled": True, "permission": PermissionLevel.USER},
    
    # 查询模块
    "whereis": {"enabled": True, "permission": PermissionLevel.USER},
    "instances": {"enabled": True, "permission": PermissionLevel.USER},
    "whois": {"enabled": True, "permission": PermissionLevel.USER},
    
    # 用户绑定模块
    "bind": {"enabled": True, "permission": PermissionLevel.USER},
    "confirm": {"enabled": True, "permission": PermissionLevel.USER},
    "unbind": {"enabled": True, "permission": PermissionLevel.USER},
    "bindinfo": {"enabled": True, "permission": PermissionLevel.USER},
    
    # 群组管理模块
    "gmembers": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "ginvite": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gkick": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gban": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gunban": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "grole": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "grequests": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gaccept": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "greject": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gannounce": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gdelannounce": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
    "gaudit": {"enabled": True, "permission": PermissionLevel.GROUP_ADMIN},
}


class CommandConfig(BaseModel):
    """单个命令的配置"""
    enabled: bool = True
    permission: int = Field(default=0, ge=0, le=2)  # 0=USER, 1=GROUP_ADMIN, 2=SUPERUSER
    
    def get_permission_level(self) -> PermissionLevel:
        return PermissionLevel(self.permission)


class GroupConfig(BaseModel):
    qq_group_id: str
    default_vrc_group: Optional[str] = None
    notify_enabled: bool = False
    admin_ops_enabled: bool = True
    allow_user_bind: bool = True
    
    # 命令配置：command_name -> CommandConfig
    commands: Dict[str, CommandConfig] = Field(default_factory=dict)
    
    def model_post_init(self, __context):
        """模型初始化后，确保所有命令都有默认配置"""
        for cmd_name, defaults in COMMAND_DEFAULTS.items():
            if cmd_name not in self.commands:
                self.commands[cmd_name] = CommandConfig(
                    enabled=defaults["enabled"],
                    permission=defaults["permission"].value,
                )
    
    def is_command_enabled(self, command_name: str) -> bool:
        """检查命令是否启用"""
        if command_name in self.commands:
            return self.commands[command_name].enabled
        # 如果命令不在配置中，使用默认值
        return COMMAND_DEFAULTS.get(command_name, {}).get("enabled", False)
    
    def get_command_permission(self, command_name: str) -> PermissionLevel:
        """获取命令的权限要求"""
        if command_name in self.commands:
            return self.commands[command_name].get_permission_level()
        # 如果命令不在配置中，使用默认值
        defaults = COMMAND_DEFAULTS.get(command_name, {})
        return defaults.get("permission", PermissionLevel.USER)
    
    def set_command_enabled(self, command_name: str, enabled: bool):
        """设置命令启用状态"""
        if command_name not in self.commands:
            self.commands[command_name] = CommandConfig()
        self.commands[command_name].enabled = enabled
    
    def set_command_permission(self, command_name: str, permission: PermissionLevel):
        """设置命令权限要求"""
        if command_name not in self.commands:
            self.commands[command_name] = CommandConfig()
        self.commands[command_name].permission = permission.value


class GroupConfigStore:
    def __init__(self):
        self._file = get_data_dir("vrc_toolbot") / "group_configs.json"
        self._configs: dict[str, GroupConfig] = {}
        self._load()

    def _load(self):
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text(encoding="utf-8"))
                self._configs = {
                    k: GroupConfig(**v) for k, v in data.items()
                }
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Failed to load group configs, resetting: {e}")
                self._configs = {}

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
            self._save()
        return self._configs[key]

    def set(self, config: GroupConfig):
        self._configs[config.qq_group_id] = config
        self._save()


group_config_store = GroupConfigStore()
