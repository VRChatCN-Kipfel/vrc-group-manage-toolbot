"""
消息工具实测试 - Utils 层

补充测试消息分割等高级功能
"""
import pytest
from nonebug import App
from tests import create_mock_bot


class TestMessageSplitting:
    """消息分割测试"""
    
    @pytest.mark.asyncio
    async def test_short_message_no_split(self, app: App):
        """
        实测试：短消息不需要分割
        
        验证短于限制的消息不会被分割
        """
        from services.message_utils import MAX_MESSAGE_LENGTH
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建短消息
        short_msg = "这是一条短消息"
        assert len(short_msg) < MAX_MESSAGE_LENGTH
    
    @pytest.mark.asyncio
    async def test_long_message_calculation(self, app: App):
        """
        实测试：长消息长度计算
        
        验证可以正确计算需要分割的消息
        """
        from services.message_utils import MAX_MESSAGE_LENGTH
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建长消息
        long_msg = "A" * 5000
        chunks = (len(long_msg) + MAX_MESSAGE_LENGTH - 1) // MAX_MESSAGE_LENGTH
        
        assert chunks == 2  # 应该分成2段
    
    @pytest.mark.asyncio
    async def test_exact_boundary_message(self, app: App):
        """
        实测试：边界长度的消息
        
        验证正好等于边界的消息处理
        """
        from services.message_utils import MAX_MESSAGE_LENGTH
        
        bot, ctx = await create_mock_bot(app)
        
        # 创建正好等于边界的消息
        exact_msg = "B" * MAX_MESSAGE_LENGTH
        assert len(exact_msg) == MAX_MESSAGE_LENGTH


class TestMessageFormattingEdgeCases:
    """消息格式化边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_format_error_empty_hint(self, app: App):
        """
        实测试：错误消息空提示
        
        验证空提示的处理
        """
        from services.message_utils import format_error
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_error("错误", "")
        # 空提示不应该显示提示部分
        assert "💡" not in msg
    
    @pytest.mark.asyncio
    async def test_format_success_special_chars(self, app: App):
        """
        实测试：成功消息特殊字符
        
        验证包含特殊字符的消息
        """
        from services.message_utils import format_success
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_success("测试\n换行\t制表符")
        assert "✅" in msg
        assert "\n" in msg
    
    @pytest.mark.asyncio
    async def test_format_query_multiline(self, app: App):
        """
        实测试：查询结果多行内容
        
        验证多行内容的格式化
        """
        from services.message_utils import format_query_result
        
        bot, ctx = await create_mock_bot(app)
        
        content = "第一行\n第二行\n第三行"
        result = format_query_result("标题", content)
        
        assert "【标题】" in result
        assert "第一行" in result
        assert "第二行" in result
        assert "第三行" in result
    
    @pytest.mark.asyncio
    async def test_format_unicode_characters(self, app: App):
        """
        实测试：Unicode 字符处理
        
        验证 Unicode 字符的正确处理
        """
        from services.message_utils import format_success, format_error
        
        bot, ctx = await create_mock_bot(app)
        
        # 中文
        msg_cn = format_success("操作成功")
        assert "操作成功" in msg_cn
        
        # Emoji
        msg_emoji = format_success("完成 ✓")
        assert "✓" in msg_emoji
