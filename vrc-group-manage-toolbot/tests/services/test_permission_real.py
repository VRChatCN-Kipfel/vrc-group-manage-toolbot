"""
权限服务测试 - 实测试

测试权限检查、权限级别转换等功能
"""
import pytest
from nonebug import App
from tests import create_mock_bot, get_test_group_id, get_test_user_id


class TestPermissionReal:
    """权限服务实测试"""
    
    @pytest.mark.asyncio
    async def test_permission_level_enum(self, app: App):
        """
        实测试：权限级别枚举
        
        验证所有权限级别都正确定义
        """
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证所有权限级别存在
        assert hasattr(PermissionLevel, 'UNBOUND_USER')
        assert hasattr(PermissionLevel, 'BOUND_USER')
        assert hasattr(PermissionLevel, 'UNBOUND_ADMIN')
        assert hasattr(PermissionLevel, 'BOUND_ADMIN')
        assert hasattr(PermissionLevel, 'OWNER')
        assert hasattr(PermissionLevel, 'SUPERUSER')
        
        # 验证权限级别的值
        assert PermissionLevel.UNBOUND_USER == 0
        assert PermissionLevel.BOUND_USER == 1
        assert PermissionLevel.UNBOUND_ADMIN == 2
        assert PermissionLevel.BOUND_ADMIN == 3
        assert PermissionLevel.OWNER == 4
        assert PermissionLevel.SUPERUSER == 5
    
    @pytest.mark.asyncio
    async def test_permission_level_comparison(self, app: App):
        """
        实测试：权限级别比较
        
        验证权限级别可以正确比较
        """
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证权限级别的大小关系
        assert PermissionLevel.UNBOUND_USER < PermissionLevel.BOUND_USER
        assert PermissionLevel.BOUND_USER < PermissionLevel.UNBOUND_ADMIN
        assert PermissionLevel.UNBOUND_ADMIN < PermissionLevel.BOUND_ADMIN
        assert PermissionLevel.BOUND_ADMIN < PermissionLevel.OWNER
        assert PermissionLevel.OWNER < PermissionLevel.SUPERUSER
        
        # 验证相等性
        assert PermissionLevel.UNBOUND_USER == PermissionLevel.UNBOUND_USER
        assert PermissionLevel.SUPERUSER != PermissionLevel.UNBOUND_USER
    
    @pytest.mark.asyncio
    async def test_check_command_permission_function_exists(self, app: App):
        """
        实测试：check_command_permission 函数存在
        
        验证权限检查函数已定义
        """
        from services.permission import check_command_permission
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证函数存在且可调用
        assert callable(check_command_permission)
    
    @pytest.mark.asyncio
    async def test_permission_config_defaults(self, app: App):
        """
        实测试：权限配置默认值
        
        验证命令的默认权限配置
        """
        from services.group_config import COMMAND_DEFAULTS
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证每个命令都有权限配置
        for cmd_name, cmd_config in COMMAND_DEFAULTS.items():
            assert 'enabled' in cmd_config
            assert 'permission' in cmd_config
            
            # 获取权限配置
            perm_value = cmd_config.get('permission')
            assert perm_value is not None
            
            # 验证权限值是 PermissionLevel 类型
            assert isinstance(perm_value, PermissionLevel)
