# HTML 渲染服务使用指南

## 概述

本项目集成了 `nonebot-plugin-htmlkit` 插件，提供了强大的 HTML/Markdown 渲染为图片的功能。通过 `services/html_render.py` 中的封装，您可以轻松地在机器人中生成美观的图片消息。

## 安装依赖

依赖已添加到 `pyproject.toml`，运行以下命令安装：

```bash
pip install nonebot-plugin-htmlkit>=0.1.0
```

或使用 nb-cli：

```bash
nb plugin install nonebot-plugin-htmlkit
```

## 快速开始

### 1. 导入服务

```python
from services.html_render import html_render_service
```

### 2. 基本用法

#### 渲染纯文本

```python
image_bytes = await html_render_service.render_text(
    text="Hello World!",
    font_size=16,
    width=800,
    bg_color="#ffffff",
    text_color="#000000"
)
```

#### 渲染 Markdown

```python
markdown_content = """
# 标题

这是一段 **Markdown** 内容。

- 列表项 1
- 列表项 2
"""

image_bytes = await html_render_service.render_markdown(
    markdown_content=markdown_content,
    width=800
)
```

#### 渲染 HTML

```python
html_content = """
<div style="padding: 20px;">
    <h1>自定义 HTML</h1>
    <p>支持完整的 HTML 和 CSS</p>
</div>
"""

image_bytes = await html_render_service.render_html(
    html_content=html_content,
    width=800
)
```

#### 使用卡片样式

```python
# 创建卡片 HTML
html_content = html_render_service.create_card_style(
    title="卡片标题",
    content="<p>卡片内容</p>",
    footer="页脚信息",
    theme="light"  # 或 "dark"
)

# 渲染为图片
image_bytes = await html_render_service.render_html(
    html_content=html_content,
    width=800
)
```

### 3. 发送图片

```python
from nonebot.adapters.onebot.v11 import MessageSegment

# 在插件中发送图片
await matcher.send(MessageSegment.image(image_bytes))
```

## API 参考

### HTMLRenderService

#### render_text()

将纯文本渲染为图片。

**参数：**
- `text` (str): 要渲染的文本内容
- `font_size` (int): 字体大小，默认 16
- `width` (int): 图片宽度，默认 800
- `padding` (int): 内边距，默认 20
- `bg_color` (str): 背景颜色，默认 "#ffffff"
- `text_color` (str): 文字颜色，默认 "#000000"

**返回：** PNG 图片的字节数据 (bytes)

#### render_markdown()

将 Markdown 内容渲染为图片。

**参数：**
- `markdown_content` (str): Markdown 格式的内容
- `width` (int): 图片宽度，默认 800
- `css` (Optional[str]): 自定义 CSS 样式

**返回：** PNG 图片的字节数据 (bytes)

#### render_html()

将 HTML 内容渲染为图片。

**参数：**
- `html_content` (str): HTML 格式的内容
- `width` (int): 图片宽度，默认 800
- `css` (Optional[str]): 额外的 CSS 样式

**返回：** PNG 图片的字节数据 (bytes)

#### render_template()

使用 Jinja2 模板渲染为图片。

**参数：**
- `template_path` (Union[str, Path]): 模板文件路径
- `context` (dict): 模板上下文数据
- `width` (int): 图片宽度，默认 800
- `css` (Optional[str]): 自定义 CSS 样式

**返回：** PNG 图片的字节数据 (bytes)

#### create_card_style()

创建卡片样式的 HTML。

**参数：**
- `title` (str): 标题
- `content` (str): 内容（HTML 格式）
- `footer` (Optional[str]): 页脚信息
- `theme` (str): 主题 ("light" 或 "dark")

**返回：** HTML 字符串

## 示例插件

项目中包含了示例插件 `plugins/html_render_demo.py`，演示了各种渲染功能的使用。

### 可用命令

- `#htmldemo text` - 演示文本渲染
- `#htmldemo md` - 演示 Markdown 渲染
- `#htmldemo card` - 演示亮色主题卡片
- `#htmldemo dark` - 演示暗色主题卡片
- `#groupstatus` - 显示群组状态卡片
- `#htmlhelp` - 显示帮助信息

## 实际应用场景

### 1. 生成群组信息卡片

```python
async def show_group_info(group_id: str):
    # 获取群组信息
    group = await get_group_info(group_id)
    
    # 构建卡片内容
    content = f"""
    <p><strong>名称：</strong>{group.name}</p>
    <p><strong>成员：</strong>{group.member_count} 人</p>
    <p><strong>在线：</strong>{group.online_count} 人</p>
    """
    
    html = html_render_service.create_card_style(
        title=f"📊 {group.name}",
        content=content,
        footer=f"更新于 {datetime.now()}"
    )
    
    image = await html_render_service.render_html(html)
    return MessageSegment.image(image)
```

### 2. 生成排行榜图片

```python
async def show_leaderboard(users: list):
    # 构建 Markdown 表格
    md = "# 🏆 活跃度排行榜\n\n"
    md += "| 排名 | 用户 | 分数 |\n"
    md += "|------|------|------|\n"
    
    for i, user in enumerate(users[:10], 1):
        md += f"| {i} | {user.name} | {user.score} |\n"
    
    image = await html_render_service.render_markdown(md)
    return MessageSegment.image(image)
```

### 3. 生成公告卡片

```python
async def send_announcement(title: str, content: str):
    html = html_render_service.create_card_style(
        title=f"📢 {title}",
        content=f"<p>{content}</p>",
        footer=f"发布时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        theme="light"
    )
    
    image = await html_render_service.render_html(html)
    await bot.send_group_msg(group_id=group_id, message=MessageSegment.image(image))
```

## 注意事项

1. **首次使用需要加载字体**：第一次渲染可能会比较慢，因为需要加载字体配置
2. **图片大小限制**：建议控制图片宽度在 800-1000px 之间，避免过大
3. **中文支持**：确保系统安装了中文字体（如 Microsoft YaHei、SimHei 等）
4. **错误处理**：始终包裹 try-except 来处理可能的渲染错误
5. **性能考虑**：频繁渲染时考虑缓存生成的图片

## 故障排除

### 问题：渲染失败，提示字体相关错误

**解决方案：**
- Windows：确保系统字体正常
- Linux：安装 fontconfig 和中文字体
  ```bash
  sudo apt-get install fontconfig fonts-wqy-zenhei
  ```

### 问题：图片显示乱码

**解决方案：**
- 检查 HTML 中是否包含 `<meta charset="UTF-8">`
- 确保文本内容是 UTF-8 编码

### 问题：渲染速度慢

**解决方案：**
- 减小图片宽度
- 简化 CSS 样式
- 考虑缓存常用模板的渲染结果

## 进阶用法

### 自定义 CSS

```python
custom_css = """
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.card {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.1);
}
"""

image = await html_render_service.render_markdown(
    markdown_content=content,
    css=custom_css
)
```

### 使用 Jinja2 模板

```python
# 创建模板文件 templates/group_info.html.jinja
"""
<div class="card">
    <h1>{{ group_name }}</h1>
    <p>成员数：{{ member_count }}</p>
    {% for member in members %}
    <div class="member">{{ member.name }}</div>
    {% endfor %}
</div>
"""

# 渲染模板
image = await html_render_service.render_template(
    template_path="templates/group_info.html.jinja",
    context={
        "group_name": "测试群组",
        "member_count": 100,
        "members": [{"name": "用户1"}, {"name": "用户2"}]
    }
)
```

## 相关链接

- [nonebot-plugin-htmlkit GitHub](https://github.com/nonebot/plugin-htmlkit)
- [NoneBot2 官方文档](https://nonebot.dev/)
- [litehtml 文档](https://github.com/litehtml/litehtml)
