"""
HTML 渲染服务
基于 nonebot-plugin-htmlkit 提供便捷的图片渲染功能
"""

import markdown
from typing import Optional, Union
from pathlib import Path
import tempfile
from nonebot import logger
import aiofiles
import json

from nonebot_plugin_htmlkit import (
    text_to_pic,
    md_to_pic,
    template_to_pic,
    html_to_pic,
    template_to_html as render_template, #你说为什么，这玩意要命名成template_to_html，换个没那么误导性的名字不行吗（
)

# 定义资源路径
ASSETS_DIR = Path(__file__).parent.parent / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
CSS_DIR = ASSETS_DIR / "css"
CONFIG_DIR = Path(__file__).parent.parent / "config" / "pic"

# 主题配置缓存
_card_themes_cache: Optional[dict] = None
_text_themes_cache: Optional[dict] = None
_markdown_themes_cache: Optional[dict] = None


class HTMLRenderService:
    """HTML 渲染服务 - 提供统一的图片渲染接口"""
    
    @staticmethod
    async def _get_text_themes() -> dict:
        """异步加载文本主题配置（带缓存）"""
        global _text_themes_cache
        if _text_themes_cache is not None:
            return _text_themes_cache
        
        theme_path = CONFIG_DIR / "text.theme.json"
        try:
            async with aiofiles.open(theme_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                _text_themes_cache = json.loads(content)
                logger.debug(f"文本主题配置加载成功: {theme_path}")
        except Exception as e:
            logger.error(f"加载文本主题配置失败: {e}，使用默认配置")
            _text_themes_cache = {}
        return _text_themes_cache

    @staticmethod
    async def _get_markdown_themes() -> dict:
        """异步加载 Markdown 主题配置（带缓存）"""
        global _markdown_themes_cache
        if _markdown_themes_cache is not None:
            return _markdown_themes_cache
        
        theme_path = CONFIG_DIR / "markdown.theme.json"
        try:
            async with aiofiles.open(theme_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                _markdown_themes_cache = json.loads(content)
                logger.debug(f"Markdown 主题配置加载成功: {theme_path}")
        except Exception as e:
            logger.error(f"加载 Markdown 主题配置失败: {e}，使用默认配置")
            _markdown_themes_cache = {}
        return _markdown_themes_cache

    @staticmethod
    async def _get_card_themes() -> dict:
        global _card_themes_cache #缓存卡片配置
        if _card_themes_cache is not None:
            return _card_themes_cache
        
        theme_path = CONFIG_DIR / "card.theme.json"
        try:
            async with aiofiles.open(theme_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                _card_themes_cache = json.loads(content)
                logger.debug(f"卡片主题配置加载成功: {theme_path}")
        except Exception as e:
            logger.error(f"加载卡片主题配置失败: {e}，使用默认配置")
            _card_themes_cache = {} # 返回空字典，后续逻辑会处理 fallback
        return _card_themes_cache

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
        theme: str = "miku",
        width: int = 800,
        font_set: Optional[str] = None,  # 字体集：可以是字体名或 URL
        decorations: bool = True,
        **overrides,
    ) -> bytes:
        """
        将纯文本渲染为图片
        
        Args:
            text: 文本内容
            theme: 主题名称 ("miku", "lxgw", "code")
            width: 图片宽度
            font_set: 字体设置。如果包含 `://` 则视为 URL/路径，否则视为字体族名称
            decorations: 是否启用装饰线
            **overrides: 覆盖主题中的其他参数 (如 padding, font_size 等)
        """
        try:
            themes = await HTMLRenderService._get_text_themes()
            params = themes.get(theme, themes.get("miku", {})).copy()
            
            if not params:
                raise ValueError(f"未找到主题 '{theme}' 且无默认 'miku' 主题配置")

            # 处理 font_set 自动识别逻辑
            final_font_url = ""
            final_font_family = params.get("font_family", "sans-serif")
            
            current_font_set = font_set or params.get("font_set")
            if current_font_set:
                if "://" in current_font_set:
                    final_font_url = current_font_set
                else:
                    final_font_family = current_font_set

            # 合并覆盖参数
            params.update(overrides)
            params.update({
                "font_url": final_font_url,
                "font_family": final_font_family,
                "decorations": decorations,
            })

            # 渲染 CSS
            final_css = await render_template(
                template_path=str(CSS_DIR),
                template_name="text.css.j2",
                templates=params
            )
            
            image_bytes = await template_to_pic(
                template_path=str(TEMPLATES_DIR),
                template_name="text.html.j2",
                templates={"text": text, "css": final_css, "decorations": decorations},
                max_width=width,
                device_height=2000,
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
        theme: str = "miku",
        font_set: Optional[str] = None,
        **overrides,
    ) -> bytes:
        """
        将 Markdown 内容渲染为图片（支持主题切换）
        
        Args:
            markdown_content: Markdown 格式的内容
            width: 图片宽度
            theme: 主题名称 (默认使用 miku)
            **overrides: 覆盖主题中的其他参数
            
        Returns:
            PNG 图片的字节数据
        """
        try:
            # 1. 加载 Markdown 专属主题配置
            themes = await HTMLRenderService._get_markdown_themes()
            params = themes.get(theme, themes.get("miku", {})).copy()
            
            if not params:
                raise ValueError(f"未找到 Markdown 主题 '{theme}' 且无默认 'miku' 主题配置")

            # 2. 处理 font_set 智能识别（复用文本渲染的逻辑）
            current_font_set = font_set or params.get("font_url")
            if current_font_set and "://" in current_font_set:
                params["font_url"] = current_font_set
            elif font_set:
                # 如果不是 URL，则视为字体族名称，覆盖 font_body
                params["font_body"] = font_set

            params.update(overrides)

            # 3. 使用 Jinja2 渲染 CSS 模板
            final_css = await render_template(
                template_path=str(CSS_DIR),
                template_name="markdown.css.j2",
                templates=params
            )

            # 4. 创建临时 CSS 文件并调用 md_to_pic
            with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False, encoding='utf-8') as tmp:
                tmp.write(final_css)
                tmp_path = tmp.name
            
            try:
                image_bytes = await md_to_pic(
                    md=markdown_content, 
                    max_width=width, 
                    css_path=tmp_path
                )
            finally:
                # 清理临时文件
                Path(tmp_path).unlink(missing_ok=True)

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
            
            image_bytes = await html_to_pic(html_content, max_width=width)
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
            theme: 主题名称 ("miku", "light", "dark", "lavender", "amber", "ocean", "rose")
            width: 图片宽度
            decorations: 是否启用装饰线（渐变光带、下划线等）
        """
        try:
            # 从配置文件加载主题
            themes = await HTMLRenderService._get_card_themes()
            colors = themes.get(theme, themes.get("miku", {}))
            
            if not colors:
                raise ValueError(f"未找到主题 '{theme}' 且无默认 'miku' 主题配置")

            # 使用 Jinja2 正确渲染 CSS 模板，支持 default 过滤器等语法
            final_css = await render_template(
                template_path=str(CSS_DIR),
                template_name="card.css.j2",
                templates=colors
            )
            
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
                max_width=width,
                device_height=2000,   # 增加高度防止长内容被截断
                base_url=f"file://{ASSETS_DIR.as_posix()}/"
            )
            logger.debug(f"卡片渲染成功，图片大小: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            logger.error(f"卡片渲染失败: {e}")
            raise


# 创建全局实例
html_render_service = HTMLRenderService()
