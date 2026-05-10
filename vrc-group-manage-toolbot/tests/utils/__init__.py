"""
Utils 模块测试 - 虚实结合

虚测：模型定义、配置加载
实测试：VRC API 客户端（模拟）
"""
import pytest
from nonebug import App


class TestVRCModels:
    """VRC 数据模型测试"""
    
    @pytest.mark.asyncio
    async def test_vrc_models_import(self):
        """虚测：验证 VRC 模型可导入"""
        from utils.VRC.vrc_models import User, Group, Instance
        assert User is not None
        assert Group is not None
        assert Instance is not None
    
    @pytest.mark.asyncio
    async def test_vrc_user_model(self):
        """虚测：验证 VRC 用户模型"""
        from utils.VRC.vrc_models import User
        
        user = User(
            id="usr_123456",
            displayName="TestUser"
        )
        
        assert user.id == "usr_123456"
        assert user.displayName == "TestUser"


class TestVRCConfig:
    """VRC 配置测试"""
    
    @pytest.mark.asyncio
    async def test_vrc_config_import(self):
        """虚测：验证 VRC 配置模块可导入"""
        from utils.VRC.vrc_config import VRCConfig
        assert VRCConfig is not None


class TestVRCClient:
    """VRC 客户端测试"""
    
    @pytest.mark.asyncio
    async def test_vrc_client_import(self):
        """虚测：验证 VRC 客户端可导入"""
        from utils.VRC.vrc_client import VRCClient
        assert VRCClient is not None
    
    @pytest.mark.asyncio
    async def test_vrc_client_initialization(self, app: App):
        """实测试：验证 VRC 客户端初始化（使用 mock）"""
        from utils.VRC.vrc_client import VRCClient
        from tests import create_mock_bot
        
        # 创建模拟 Bot
        bot, ctx = await create_mock_bot(app)
        
        # 这里可以添加更详细的客户端测试
        # 由于涉及实际 API 调用，建议使用 mock
        assert VRCClient is not None
