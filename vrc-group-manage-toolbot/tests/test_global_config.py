"""
Unit tests for GlobalConfig reload
"""
import asyncio
from unittest.mock import patch

import pytest
import yaml

from services.global_config import GlobalConfig, CONFIG_DIR


class TestGlobalConfig:
    """UT-2: GlobalConfig 单元测试"""

    def test_load_default_config(self):
        """UT-2.1: 加载默认配置"""
        gc = GlobalConfig()
        assert isinstance(gc.is_blacklist_enabled, bool)
        assert isinstance(gc.is_welcome_enabled, bool)
        assert isinstance(gc.verify_code_ttl, int)
        assert isinstance(gc.is_auto_cleanup_enabled, bool)
        assert isinstance(gc.cleanup_interval, int)

    def test_verify_code_ttl_default(self):
        gc = GlobalConfig()
        assert gc.verify_code_ttl == 180

    def test_cleanup_interval_default(self):
        gc = GlobalConfig()
        assert gc.cleanup_interval == 3600

    async def test_reload_atomic_swap_features(self, temp_config_dir):
        """UT-2.2: reload() 原子替换 features"""
        yml_file = temp_config_dir / "group_features.yml"
        yml_file.write_text(
            yaml.dump({"features": {"blacklist_enabled": False, "welcome_enabled": False}}),
            encoding="utf-8",
        )
        (temp_config_dir / "binding_settings.yml").write_text(
            yaml.dump({"binding": {"verify_code_ttl": 180, "auto_cleanup_enabled": True, "cleanup_interval": 3600}}),
            encoding="utf-8",
        )

        with patch("services.global_config.CONFIG_DIR", temp_config_dir):
            gc = GlobalConfig()
            assert gc.is_blacklist_enabled is False
            assert gc.is_welcome_enabled is False

            yml_file.write_text(
                yaml.dump({"features": {"blacklist_enabled": True, "welcome_enabled": True}}),
                encoding="utf-8",
            )
            await gc.reload()
            assert gc.is_blacklist_enabled is True
            assert gc.is_welcome_enabled is True

    async def test_reload_atomic_swap_binding(self, temp_config_dir):
        """UT-2.3: reload() 原子替换 binding_settings"""
        (temp_config_dir / "group_features.yml").write_text(
            yaml.dump({"features": {"blacklist_enabled": True, "welcome_enabled": True}}),
            encoding="utf-8",
        )
        binding_file = temp_config_dir / "binding_settings.yml"
        binding_file.write_text(
            yaml.dump({"binding": {"verify_code_ttl": 180, "auto_cleanup_enabled": True, "cleanup_interval": 3600}}),
            encoding="utf-8",
        )

        with patch("services.global_config.CONFIG_DIR", temp_config_dir):
            gc = GlobalConfig()
            assert gc.cleanup_interval == 3600

            binding_file.write_text(
                yaml.dump({"binding": {"verify_code_ttl": 300, "auto_cleanup_enabled": False, "cleanup_interval": 7200}}),
                encoding="utf-8",
            )
            await gc.reload()
            assert gc.verify_code_ttl == 300
            assert gc.is_auto_cleanup_enabled is False
            assert gc.cleanup_interval == 7200

    async def test_reload_missing_file_no_crash(self, temp_config_dir):
        """UT-2.4: 缺失 YAML 文件 reload 不崩溃"""
        (temp_config_dir / "group_features.yml").write_text(
            yaml.dump({"features": {"blacklist_enabled": True}}),
            encoding="utf-8",
        )

        with patch("services.global_config.CONFIG_DIR", temp_config_dir):
            gc = GlobalConfig()
            assert gc.cleanup_interval == 3600
            await gc.reload()

    async def test_reload_corrupted_yaml_no_crash(self, temp_config_dir):
        """UT-2.5: 损坏 YAML reload 不崩溃"""
        (temp_config_dir / "group_features.yml").write_text("invalid: [broken", encoding="utf-8")
        (temp_config_dir / "binding_settings.yml").write_text(
            yaml.dump({"binding": {"cleanup_interval": 3600}}),
            encoding="utf-8",
        )

        with patch("services.global_config.CONFIG_DIR", temp_config_dir):
            gc = GlobalConfig()
            await gc.reload()
            assert gc.cleanup_interval == 3600

    async def test_reload_lock_protects_concurrent(self, temp_config_dir):
        """UT-2.6: reload() 受 _lock 保护"""
        (temp_config_dir / "group_features.yml").write_text(
            yaml.dump({"features": {"blacklist_enabled": True}}),
            encoding="utf-8",
        )
        (temp_config_dir / "binding_settings.yml").write_text(
            yaml.dump({"binding": {"cleanup_interval": 3600}}),
            encoding="utf-8",
        )

        with patch("services.global_config.CONFIG_DIR", temp_config_dir):
            gc = GlobalConfig()
            await asyncio.gather(gc.reload(), gc.reload(), gc.reload())

    async def test_property_reads_not_blocked_by_lock(self, temp_config_dir):
        """UT-2.7: 属性读取不被 _lock 阻塞"""
        (temp_config_dir / "group_features.yml").write_text(
            yaml.dump({"features": {"blacklist_enabled": True, "welcome_enabled": True}}),
            encoding="utf-8",
        )
        (temp_config_dir / "binding_settings.yml").write_text(
            yaml.dump({"binding": {"verify_code_ttl": 180, "auto_cleanup_enabled": True, "cleanup_interval": 3600}}),
            encoding="utf-8",
        )

        with patch("services.global_config.CONFIG_DIR", temp_config_dir):
            gc = GlobalConfig()
            async def read_props():
                for _ in range(50):
                    _ = gc.is_blacklist_enabled
                    _ = gc.is_welcome_enabled
                    _ = gc.verify_code_ttl
                    _ = gc.is_auto_cleanup_enabled
                    _ = gc.cleanup_interval
                    await asyncio.sleep(0)

            await asyncio.gather(gc.reload(), read_props())
