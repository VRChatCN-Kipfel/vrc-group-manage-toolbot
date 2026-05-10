"""
群组配置管理测试 - 实测试示例

展示如何使用 nonebug 进行完整的配置管理测试
"""
import pytest
from nonebug import App
from tests import create_mock_bot, get_test_group_id


class TestGroupConfigReal:
    """群组配置实测试"""
    
    @pytest.mark.asyncio
    async def test_config_persistence_with_mock_bot(self, app: App, cleanup_after_test):
        """
        实测试：使用 mock bot 测试配置持久化
        
        这个测试展示了：
        1. 创建 mock bot
        2. 修改配置
        3. 验证持久化
        4. 自动清理（通过 cleanup_after_test fixture）
        """
        from services.group_config import group_config_store
        from services.permission import PermissionLevel
        
        # 创建 mock bot
        bot, ctx = await create_mock_bot(app)
        
        # 获取测试群 ID
        test_group_id = get_test_group_id()
        
        # 获取配置
        config = group_config_store.get(test_group_id)
        assert config is not None
        
        # 记录原始状态
        original_gban_status = config.is_command_enabled("gban")
        original_whereis_perm = config.get_command_permission("whereis")
        
        # 修改配置
        config.set_command_enabled("gban", not original_gban_status)
        config.set_command_permission("whereis", PermissionLevel.BOUND_ADMIN)
        
        # 保存
        group_config_store.set(config)
        
        # 重新加载验证
        reloaded = group_config_store.get(test_group_id)
        assert reloaded.is_command_enabled("gban") == (not original_gban_status)
        assert reloaded.get_command_permission("whereis") == PermissionLevel.BOUND_ADMIN
        
        # 注意：不需要手动清理，cleanup_after_test 会自动执行
    
    @pytest.mark.asyncio
    async def test_multiple_groups_isolation(self, app: App):
        """
        实测试：验证多个群组配置隔离
        
        确保不同群的配置互不影响
        """
        from services.group_config import group_config_store
        
        bot, ctx = await create_mock_bot(app)
        
        group1_id = get_test_group_id(1)
        group2_id = get_test_group_id(2)
        
        # 分别修改两个群的配置
        config1 = group_config_store.get(group1_id)
        config1.set_command_enabled("gban", False)
        group_config_store.set(config1)
        
        config2 = group_config_store.get(group2_id)
        config2.set_command_enabled("gban", True)
        group_config_store.set(config2)
        
        # 验证隔离
        reloaded1 = group_config_store.get(group1_id)
        reloaded2 = group_config_store.get(group2_id)
        
        assert reloaded1.is_command_enabled("gban") == False
        assert reloaded2.is_command_enabled("gban") == True
        
        # 清理
        config1.commands.clear()
        config2.commands.clear()
        group_config_store.set(config1)
        group_config_store.set(config2)
    
    @pytest.mark.asyncio
    async def test_config_default_values(self, app: App):
        """
        实测试：验证新群组配置的默认值
        
        确保新创建的群组有正确的默认配置
        """
        from services.group_config import group_config_store
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 使用一个新的群 ID
        new_group_id = get_test_group_id(99)
        
        # 获取配置（应该是新创建的）
        config = group_config_store.get(new_group_id)
        
        # 验证默认值
        assert config is not None
        assert len(config.commands) > 0
        
        # 验证关键命令的默认状态
        whereis_enabled = config.is_command_enabled("whereis")
        whereis_perm = config.get_command_permission("whereis")
        
        assert isinstance(whereis_enabled, bool)
        assert isinstance(whereis_perm, PermissionLevel)
        
        # 清理
        config.commands.clear()
        group_config_store.set(config)
