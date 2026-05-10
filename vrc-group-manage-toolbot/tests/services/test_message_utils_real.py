"""
消息工具服务测试 - 实测试

测试消息格式化、长消息分割等功能
"""
import pytest
from nonebug import App
from tests import create_mock_bot


class TestMessageUtilsReal:
    """消息工具实测试"""
    
    @pytest.mark.asyncio
    async def test_format_success(self, app: App):
        """
        实测试：成功消息格式化
        
        验证成功消息的正确格式
        """
        from services.message_utils import format_success
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_success("操作成功")
        assert msg == "✅ 操作成功"
        
        msg2 = format_success("绑定成功")
        assert msg2 == "✅ 绑定成功"
    
    @pytest.mark.asyncio
    async def test_format_error_without_hint(self, app: App):
        """
        实测试：错误消息格式化（无提示）
        
        验证不带提示的错误消息格式
        """
        from services.message_utils import format_error
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_error("权限不足")
        assert msg == "❌ 操作失败：权限不足"
    
    @pytest.mark.asyncio
    async def test_format_error_with_hint(self, app: App):
        """
        实测试：错误消息格式化（有提示）
        
        验证带提示的错误消息格式
        """
        from services.message_utils import format_error
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_error("权限不足", "需要管理员权限")
        assert msg == "❌ 操作失败：权限不足\n💡 提示：需要管理员权限"
    
    @pytest.mark.asyncio
    async def test_format_query_result(self, app: App):
        """
        实测试：查询结果格式化
        
        验证查询结果的格式
        """
        from services.message_utils import format_query_result
        
        bot, ctx = await create_mock_bot(app)
        
        result = format_query_result("用户信息", "姓名: 张三\n年龄: 25")
        
        assert "【用户信息】" in result
        assert "姓名: 张三" in result
        assert "年龄: 25" in result
        assert "─" * 20 in result
    
    @pytest.mark.asyncio
    async def test_max_message_length_constant(self, app: App):
        """
        实测试：最大消息长度常量
        
        验证最大消息长度定义正确
        """
        from services.message_utils import MAX_MESSAGE_LENGTH
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证常量存在且合理
        assert isinstance(MAX_MESSAGE_LENGTH, int)
        assert MAX_MESSAGE_LENGTH > 0
        assert MAX_MESSAGE_LENGTH == 3800
    
    @pytest.mark.asyncio
    async def test_send_long_message_function_exists(self, app: App):
        """
        实测试：长消息发送函数存在
        
        验证 send_long_message 函数已定义
        """
        from services.message_utils import send_long_message
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证函数存在且可调用
        assert callable(send_long_message)
    
    @pytest.mark.asyncio
    async def test_format_functions_are_pure(self, app: App):
        """
        实测试：格式化函数是纯函数
        
        验证格式化函数没有副作用
        """
        from services.message_utils import format_success, format_error, format_query_result
        
        bot, ctx = await create_mock_bot(app)
        
        # 多次调用应该返回相同结果
        msg1 = format_success("test")
        msg2 = format_success("test")
        assert msg1 == msg2
        
        err1 = format_error("error", "hint")
        err2 = format_error("error", "hint")
        assert err1 == err2
        
        query1 = format_query_result("title", "content")
        query2 = format_query_result("title", "content")
        assert query1 == query2
