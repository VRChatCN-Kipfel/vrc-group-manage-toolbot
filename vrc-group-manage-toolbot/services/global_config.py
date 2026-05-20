"""
全局配置加载服务
负责从 config 目录加载 YAML 配置文件并提供统一访问接口
"""
import yaml
from pathlib import Path
from nonebot import logger

CONFIG_DIR = Path(__file__).parent.parent / "config"

class GlobalConfig:
    def __init__(self):
        self.features = {}
        self.binding_settings = {}
        self._load_all()

    def _load_yaml(self, filename: str) -> dict:
        file_path = CONFIG_DIR / filename
        if not file_path.exists():
            logger.warning(f"配置文件不存在: {file_path}，使用默认空配置")
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载配置文件 {filename} 失败: {e}")
            return {}

    def _load_all(self):
        # 加载功能开关
        features_data = self._load_yaml("group_features.yml")
        self.features = features_data.get("features", {})

        # 加载绑定设置
        binding_data = self._load_yaml("binding_settings.yml")
        self.binding_settings = binding_data.get("binding", {})
        
        logger.info("全局配置加载完成")

    @property
    def is_blacklist_enabled(self) -> bool:
        return self.features.get("blacklist_enabled", True)

    @property
    def is_welcome_enabled(self) -> bool:
        return self.features.get("welcome_enabled", True)

    @property
    def verify_code_ttl(self) -> int:
        return self.binding_settings.get("verify_code_ttl", 180)

    @property
    def is_auto_cleanup_enabled(self) -> bool:
        return self.binding_settings.get("auto_cleanup_enabled", True)

    @property
    def cleanup_interval(self) -> int:
        return self.binding_settings.get("cleanup_interval", 3600)

# 实例化全局配置对象
global_config = GlobalConfig()
