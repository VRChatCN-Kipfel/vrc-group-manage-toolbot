# HTML 渲染服务使用指南

本文档介绍了 `vrc-group-manage-toolbot` 中基于 `nonebot-plugin-htmlkit` 的 HTML 渲染服务。该服务支持将文本、Markdown、HTML 字符串以及预设模板渲染为精美的图片，适用于机器人公告、通知及信息展示。

## 📁 目录结构

```text
vrc-group-manage-toolbot/
├── assets/
│   ├── css/          # CSS 模板文件 (.j2)
│   └── templates/    # HTML 模板文件 (.j2)
├── config/pic/       # 主题配色配置文件 (.json)
└── services/
    └── html_render.py # 核心渲染服务逻辑
```

---

## 🚀 快速开始

### 1. 初始化服务
在插件中导入全局实例：
```python
from services.html_render import html_render_service
```

### 2. 基础调用示例
```python
# 渲染一张卡片图片
image_bytes = await html_render_service.render_card(
    title="🎉 欢迎加入",
    content="<p>这里是 VRChat 群组管理工具。</p>",
    theme="miku"
)

# 发送图片 (以 OneBot V11 为例)
from nonebot.adapters.onebot.v11 import MessageSegment
await bot.send_group_msg(group_id=123456, message=MessageSegment.image(image_bytes))
```

---

## 🎨 核心功能接口

### 1. 卡片渲染 (`render_card`)
适用于带有标题、内容和页脚的标准化信息展示。

**函数签名：**
```python
async def render_card(
    title: str,
    content: str,
    footer: Optional[str] = None,
    theme: str = "miku",
    width: int = 800,
    decorations: bool = True
) -> bytes
```

**可用主题 (Theme):**
*   `miku`: 初音未来绿（默认）
*   `light`: 浅色明亮
*   `dark`: 深色护眼
*   `lavender`: 梦幻薰衣草紫
*   `amber`: 温暖琥珀金
*   `ocean`: 深邃海洋蓝
*   `rose`: 浪漫玫瑰粉

---

### 2. 文本渲染 (`render_text`)
适用于纯文本或富文本内容的展示，支持星空背景和玻璃态面板。

**函数签名：**
```python
async def render_text(
    text: str,
    theme: str = "miku",
    width: int = 800,
    font_set: Optional[str] = None,
    decorations: bool = True,
    **overrides
) -> bytes
```

**智能字体识别 (`font_set`):**
*   如果字符串包含 `://` (如 `https://...` 或 `file://...`)，则视为字体 URL。
*   否则，视为字体族名称 (Font Family)。

**可用主题 (Theme):**
*   `miku`, `lxgw` (霞鹜文楷), `code` (JetBrains Mono)
*   `violet`, `amber`, `frost`, `cyber`, `minimal`

---

### 3. Markdown 渲染 (`render_markdown`)
直接将 Markdown 语法转换为图片。

```python
image_bytes = await html_render_service.render_markdown(
    markdown_content="# 标题\n- 列表项",
    width=800
)
```

---

### 4. 原生 HTML 渲染 (`render_html`)
提供最大的灵活性，允许传入完整的 HTML 字符串。

```python
html_str = "<div style='color:red'>自定义内容</div>"
image_bytes = await html_render_service.render_html(html_str, width=800)
```

---

## ⚙️ 主题配置系统

所有配色方案均外置在 `config/pic/` 目录下的 JSON 文件中，无需修改代码即可扩展新主题。

### 卡片主题 (`card.theme.json`)
定义了背景色、面板色、边框色及三阶强调色（Accent Colors）。

### 文本主题 (`text.theme.json`)
除了基础配色外，还支持预设字体集（`font_set`）和排版参数（`padding`, `font_size`）。

**新增主题步骤：**
1. 在对应的 `.json` 文件中添加一个新的键值对。
2. 确保包含所有必填字段（如 `bg_color`, `accent_1_rgb` 等）。
3. 重启 Bot 或在支持下一次渲染时自动加载。

---

## 💡 高级技巧

### 动态覆盖参数
在 `render_text` 中，你可以使用 `**overrides` 临时修改主题中的任何属性：
```python
# 在 miku 主题基础上，临时增大内边距并关闭装饰线
await html_render_service.render_text(
    "紧急通知", 
    theme="miku", 
    padding=60, 
    decorations=False
)
```

### 自定义字体
利用 `font_set` 参数加载特殊字体：
```python
# 加载网络字体
await html_render_service.render_text(
    "Code Log", 
    theme="code", 
    font_set="https://fonts.gstatic.com/s/roboto/..."
)
```

---

## 📝 注意事项

1.  **资源路径**：渲染引擎依赖 `base_url` 来定位本地资源，请确保 `assets` 目录路径正确。
2.  **性能优化**：主题配置文件在首次加载后会自动缓存，修改配置后需重启服务或通过定时任务重载。
3.  **内容截断**：如果内容过长，请适当增加 `device_height` 参数（目前默认设为 2000px）。
