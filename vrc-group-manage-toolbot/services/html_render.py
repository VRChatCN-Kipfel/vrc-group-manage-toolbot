"""
HTML 渲染服务
基于 nonebot-plugin-htmlkit 提供便捷的图片渲染功能
"""

from typing import Optional, Union
from pathlib import Path
from nonebot import logger
import aiofiles

from nonebot_plugin_htmlkit import (
    text_to_pic,
    md_to_pic,
    template_to_pic,
    html_to_pic,
)

# 定义资源路径
ASSETS_DIR = Path(__file__).parent.parent / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
CSS_DIR = ASSETS_DIR / "css"


class HTMLRenderService:
    """HTML 渲染服务 - 提供统一的图片渲染接口"""
    
    @staticmethod
    async def _read_css(css_filename: str) -> str:
        """读取 CSS 文件内容"""
        css_path = CSS_DIR / css_filename
        if not css_path.exists():
            return ""
        async with aiofiles.open(css_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    @staticmethod
    async def render_text(
        text: str,
        font_size: int = 16,
        width: int = 800,
        padding: int = 20,
        bg_color: str = "#ffffff",
        text_color: str = "#000000",
    ) -> bytes:
        """
        将纯文本渲染为图片
        """
        try:
            css_template = await HTMLRenderService._read_css("text.css.j2")
            # 简单的模板渲染（text.css自备变量）
            final_css = css_template.format(
                padding=padding,
                bg_color=bg_color,
                font_size=font_size,
                text_color=text_color
            )
            
            image_bytes = await template_to_pic(
                template_path=str(TEMPLATES_DIR),
                template_name="text.html.j2",
                templates={"text": text, "css": final_css},
                width=width,
                base_url=f"file://{ASSETS_DIR.as_posix()}/"
            )
            logger.debug(f"文本渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"文本渲染失败: {e}")
            raise
    
    @staticmethod
    async def render_markdown(
        markdown_content: str,
        width: int = 800,
        css_filename: str = "markdown.css",
    ) -> bytes:
        """
        将 Markdown 内容渲染为图片
        
        Args:
            markdown_content: Markdown 格式的内容
            width: 图片宽度
            css_filename: CSS 文件名 (位于 assets/css/ 目录下)
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            final_css = await HTMLRenderService._read_css(css_filename)
            image_bytes = await md_to_pic(markdown_content, width=width, css=final_css)
            logger.debug(f"Markdown 渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"Markdown 渲染失败: {e}")
            raise
    
    @staticmethod
    async def render_html(
        html_content: str,
        width: int = 800,
        css_filename: Optional[str] = None,
    ) -> bytes:
        """
        将 HTML 内容渲染为图片
        
        Args:
            html_content: HTML 格式的内容
            width: 图片宽度
            css_filename: CSS 文件名 (位于 assets/css/ 目录下，可选)
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            final_css = ""
            if css_filename:
                final_css = await HTMLRenderService._read_css(css_filename)
                
            # 如果提供了额外 CSS，注入到 HTML 中
            if final_css:
                if "<style>" in html_content:
                    # 在最后一个 </style> 前插入
                    html_content = html_content.replace(
                        "</style>",
                        f"{final_css}</style>",
                        1
                    )
                else:
                    # 在 <head> 中添加 style
                    if "<head>" in html_content:
                        html_content = html_content.replace(
                            "<head>",
                            f"<head><style>{final_css}</style>"
                        )
                    else:
                        html_content = f"<style>{final_css}</style>{html_content}"
            
            image_bytes = await html_to_pic(html_content, width=width)
            logger.debug(f"HTML 渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"HTML 渲染失败: {e}")
            raise
    
    @staticmethod
    async def render_card(
        title: str,
        content: str,
        footer: Optional[str] = None,
        theme: str = "miku",
        width: int = 800,
        decorations: bool = True,
    ) -> bytes:
        """
        使用卡片模板渲染为图片
        
        Args:
            title: 卡片标题
            content: 卡片内容（HTML格式）
            footer: 页脚信息（可选）
            theme: 主题名称 ("miku", "light", "dark")
            width: 图片宽度
            decorations: 是否启用装饰线（渐变光带、下划线等）
        """
        try:
            # 主题配色逻辑保留在 Python 层，方便动态切换
            themes = {
                "miku": {  # 初音未来主题（默认）
                    "bg_color": "#08080c",                    # 深邃黑
                    "card_bg": "rgba(10, 18, 30, 0.42)",     # 半透明深蓝
                    "border_color": "rgba(57, 197, 187, 0.22)",  # 初音绿半透明
                    "title_color": "#7fffd4",                # 薄荷绿
                    "text_color": "#d0f0ee",                 # 浅青白
                    "footer_color": "#5aaeb0",               # 青绿色
                    # CSS 变量系统 - 强调色（使用默认值）
                    "accent_1": "#7fffd4",                   # 薄荷绿
                    "accent_2": "#39c5bb",                   # 初音绿
                    "accent_3": "#40e0d0",                   # 湖水蓝
                    "accent_1_rgb": "127, 255, 212",
                    "accent_2_rgb": "57, 197, 187",
                    "accent_3_rgb": "64, 224, 208",
                },
                "light": {
                    "bg_color": "#ffffff", 
                    "card_bg": "rgba(248, 249, 250, 0.9)",
                    "border_color": "rgba(57, 197, 187, 0.3)",
                    "title_color": "#2c3e50", 
                    "text_color": "#333333",
                    "footer_color": "#666666",
                    "accent_1": "#7fffd4",
                    "accent_2": "#39c5bb",
                    "accent_3": "#40e0d0",
                    "accent_1_rgb": "127, 255, 212",
                    "accent_2_rgb": "57, 197, 187",
                    "accent_3_rgb": "64, 224, 208",
                },
                "dark": {
                    "bg_color": "#1a1a1a", 
                    "card_bg": "rgba(45, 45, 45, 0.85)",
                    "border_color": "rgba(57, 197, 187, 0.2)",
                    "title_color": "#ecf0f1", 
                    "text_color": "#bdc3c7",
                    "footer_color": "#95a5a6",
                    "accent_1": "#7fffd4",
                    "accent_2": "#39c5bb",
                    "accent_3": "#40e0d0",
                    "accent_1_rgb": "127, 255, 212",
                    "accent_2_rgb": "57, 197, 187",
                    "accent_3_rgb": "64, 224, 208",
                }
            }
            colors = themes.get(theme, themes["miku"])
            
            css_template = await HTMLRenderService._read_css("card.css.j2")
            final_css = css_template.format(**colors)
            
            image_bytes = await template_to_pic(
                template_path=str(TEMPLATES_DIR),
                template_name="card.html.j2",
                templates={
                    "title": title,
                    "content": content,
                    "footer": footer,
                    "css": final_css,
                    "decorations": decorations,
                },
                width=width,
                base_url=f"file://{ASSETS_DIR.as_posix()}/"
            )
            logger.debug(f"卡片渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"卡片渲染失败: {e}")
            raise


# 创建全局实例
html_render_service = HTMLRenderService()
