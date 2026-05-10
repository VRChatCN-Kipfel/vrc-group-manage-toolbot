"""
VRChat 群组管理机器人测试套件

采用虚实结合的测试策略：
- 虚测：模块导入、命令合法性检查、配置验证等
- 实测试：模拟 Bot 环境、功能交互测试等

提供测试工具函数（供测试代码和 conftest 使用）
"""
import sys
from pathlib import Path
from typing import Optional
from nonebug import App

# ============================================================================
# 路径配置（模块导入时立即执行）
# ============================================================================

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# ============================================================================
# 测试工具函数（纯函数，无副作用）
# ============================================================================

async def create_mock_bot(app: App, self_id: str = "2085564820"):
    """
    创建模拟 Bot 实例
    
    Args:
        app: nonebug App 实例
        self_id: Bot 的 QQ 号，默认为超级用户
        
    Returns:
        (bot, ctx) 元组
        
    Example:
        bot, ctx = await create_mock_bot(app)
    """
    async with app.test_api() as ctx:
        bot = ctx.create_bot(self_id=self_id)
        return bot, ctx


def get_test_group_id(index: int = 1) -> str:
    """
    生成测试用的群 ID（纯数字，符合 OneBot 规范）
    
    Args:
        index: 序号，用于生成不同的群 ID
        
    Returns:
        纯数字字符串格式的群 ID
        
    Example:
        group_id = get_test_group_id(1)  # "100000001"
    """
    return f"10000000{index}"


def get_test_user_id(index: int = 1) -> str:
    """
    生成测试用的用户 ID
    
    Args:
        index: 序号，用于生成不同的用户 ID
        
    Returns:
        纯数字字符串格式的用户 ID
    """
    return f"100000000{index}"
