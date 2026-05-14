"""
HTML 渲染服务
基于 nonebot-plugin-htmlkit 提供便捷的图片渲染功能
"""

from typing import Optional, Union
from pathlib import Path
from nonebot import logger

from nonebot_plugin_htmlkit import (
    text_to_pic,
    md_to_pic,
    template_to_pic,
    html_to_pic,
    debug_html_to_pic
)


class HTMLRenderService:
    """HTML 渲染服务 - 提供统一的图片渲染接口"""
    
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
        
        Args:
            text: 要渲染的文本内容
            font_size: 字体大小
            width: 图片宽度
            padding: 内边距
            bg_color: 背景颜色
            text_color: 文字颜色
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            # 构建简单的 HTML 模板
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        margin: 0;
                        padding: {padding}px;
                        background-color: {bg_color};
                        font-size: {font_size}px;
                        color: {text_color};
                        font-family: "Microsoft YaHei", "SimHei", sans-serif;
                        line-height: 1.6;
                    }}
                    .content {{
                        width: {width - 2 * padding}px;
                        word-wrap: break-word;
                    }}
                </style>
            </head>
            <body>
                <div class="content">
                    {text.replace(chr(10), "<br>")}
                </div>
            </body>
            </html>
            """
            
            image_bytes = await html_to_pic(html_content, width=width)
            logger.debug(f"文本渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"文本渲染失败: {e}")
            raise
    
    @staticmethod
    async def render_markdown(
        markdown_content: str,
        width: int = 800,
        css: Optional[str] = None,
    ) -> bytes:
        """
        将 Markdown 内容渲染为图片
        
        Args:
            markdown_content: Markdown 格式的内容
            width: 图片宽度
            css: 自定义 CSS 样式
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            # 默认 CSS 样式
            default_css = """
            body {
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                line-height: 1.6;
                padding: 20px;
                background-color: #ffffff;
                color: #333333;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: "Consolas", "Monaco", monospace;
            }
            pre {
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            blockquote {
                border-left: 4px solid #ddd;
                padding-left: 15px;
                color: #666;
                margin: 10px 0;
            }
            """
            
            final_css = css if css else default_css
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
        css: Optional[str] = None,
    ) -> bytes:
        """
        将 HTML 内容渲染为图片
        
        Args:
            html_content: HTML 格式的内容
            width: 图片宽度
            css: 额外的 CSS 样式（会追加到 HTML 中）
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            # 如果提供了额外 CSS，注入到 HTML 中
            if css:
                if "<style>" in html_content:
                    # 在最后一个 </style> 前插入
                    html_content = html_content.replace(
                        "</style>",
                        f"{css}</style>",
                        1
                    )
                else:
                    # 在 <head> 中添加 style
                    if "<head>" in html_content:
                        html_content = html_content.replace(
                            "<head>",
                            f"<head><style>{css}</style>"
                        )
                    else:
                        html_content = f"<style>{css}</style>{html_content}"
            
            image_bytes = await html_to_pic(html_content, width=width)
            logger.debug(f"HTML 渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"HTML 渲染失败: {e}")
            raise
    
    @staticmethod
    async def render_template(
        template_path: Union[str, Path],
        context: dict,
        width: int = 800,
        css: Optional[str] = None,
    ) -> bytes:
        """
        使用 Jinja2 模板渲染为图片
        
        Args:
            template_path: 模板文件路径
            context: 模板上下文数据
            width: 图片宽度
            css: 自定义 CSS 样式
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            image_bytes = await template_to_pic(
                template_path=str(template_path),
                context=context,
                width=width,
                css=css,
            )
            logger.debug(f"模板渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            raise
    
    @staticmethod
    def create_card_style(
        title: str,
        content: str,
        footer: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """
        创建卡片样式的 HTML
        
        Args:
            title: 标题
            content: 内容
            footer: 页脚信息
            theme: 主题 (light/dark)
            
        Returns:
            HTML 字符串
        """
        # 主题配色
        themes = {
            "light": {
                "bg": "#ffffff",
                "card_bg": "#f8f9fa",
                "title_color": "#2c3e50",
                "text_color": "#333333",
                "footer_color": "#666666",
                "border_color": "#e0e0e0",
            },
            "dark": {
                "bg": "#1a1a1a",
                "card_bg": "#2d2d2d",
                "title_color": "#ecf0f1",
                "text_color": "#bdc3c7",
                "footer_color": "#95a5a6",
                "border_color": "#404040",
            }
        }
        
        colors = themes.get(theme, themes["light"])
        
        footer_html = ""
        if footer:
            footer_html = f"""
            <div class="footer">{footer}</div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: {colors['bg']};
                    font-family: "Microsoft YaHei", "SimHei", sans-serif;
                }}
                .card {{
                    background-color: {colors['card_bg']};
                    border: 1px solid {colors['border_color']};
                    border-radius: 10px;
                    padding: 20px;
                    max-width: 760px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .title {{
                    font-size: 24px;
                    font-weight: bold;
                    color: {colors['title_color']};
                    margin-bottom: 15px;
                    border-bottom: 2px solid {colors['border_color']};
                    padding-bottom: 10px;
                }}
                .content {{
                    font-size: 16px;
                    color: {colors['text_color']};
                    line-height: 1.8;
                    margin-bottom: 15px;
                }}
                .footer {{
                    font-size: 14px;
                    color: {colors['footer_color']};
                    text-align: right;
                    margin-top: 15px;
                    padding-top: 10px;
                    border-top: 1px solid {colors['border_color']};
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="title">{title}</div>
                <div class="content">{content}</div>
                {footer_html}
            </div>
        </body>
        </html>
        """
        
        return html


# 创建全局实例
html_render_service = HTMLRenderService()
