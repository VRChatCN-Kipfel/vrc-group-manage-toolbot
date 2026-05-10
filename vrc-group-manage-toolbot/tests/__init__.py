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

async def create_mock_bot(app: App, self_id: str = "1000000000"):  # 测试用Bot QQ号（非真实账号）
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


# ============================================================================
# 消息事件模拟工具（用于 nonebug 测试）
# ============================================================================

def create_group_message_event(
    user_id: str,
    group_id: str,
    message: str,
    role: str = "member",
    sender_nick: str = "TestUser",
):
    """
    创建群聊消息事件
    
    Args:
        user_id: 发送者 QQ 号
        group_id: 群号
        message: 消息内容
        role: 角色 (owner/admin/member)
        sender_nick: 发送者昵称
        
    Returns:
        事件字典，可用于 ctx.receive()
    """
    from nonebot.adapters.onebot.v11 import Message
    
    return {
        "post_type": "message",
        "message_type": "group",
        "sub_type": "normal",
        "time": 1234567890,
        "self_id": 1000000000,
        "user_id": int(user_id),
        "message_id": 1,
        "group_id": int(group_id),
        "message": Message(message),
        "raw_message": message,
        "font": 0,
        "sender": {
            "user_id": int(user_id),
            "nickname": sender_nick,
            "card": "",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "role": role,
        },
    }


def create_private_message_event(
    user_id: str,
    message: str,
    sender_nick: str = "TestUser",
):
    """
    创建私聊消息事件
    
    Args:
        user_id: 发送者 QQ 号
        message: 消息内容
        sender_nick: 发送者昵称
        
    Returns:
        事件字典，可用于 ctx.receive()
    """
    from nonebot.adapters.onebot.v11 import Message
    
    return {
        "post_type": "message",
        "message_type": "private",
        "sub_type": "friend",
        "time": 1234567890,
        "self_id": 1000000000,
        "user_id": int(user_id),
        "message_id": 1,
        "message": Message(message),
        "raw_message": message,
        "font": 0,
        "sender": {
            "user_id": int(user_id),
            "nickname": sender_nick,
            "sex": "unknown",
            "age": 0,
        },
    }
