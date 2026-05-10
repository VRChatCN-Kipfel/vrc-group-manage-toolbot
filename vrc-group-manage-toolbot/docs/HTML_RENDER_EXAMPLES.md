# HTML 渲染服务 - 使用示例

本文档提供了一些在实际场景中使用 `html_render_service` 的完整示例。

## 示例 1：生成用户信息卡片

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from services.html_render import html_render_service
from services.user_binding import user_binding_store


usercard = on_command("usercard", priority=5)


@usercard.handle()
async def handle_usercard(bot: Bot, event: GroupMessageEvent):
    """生成用户信息卡片"""
    
    # 获取用户的绑定信息
    binding = user_binding_store.get_by_qq(str(event.get_user_id()))
    
    if not binding:
        await usercard.finish("❌ 您尚未绑定 VRChat 账号")
    
    # 构建卡片内容
    title = f"👤 {binding.vrc_display_name}"
    
    content = f"""
    <p><strong>VRChat ID：</strong>{binding.vrc_user_id}</p>
    <p><strong>QQ 号：</strong>{binding.qq_id}</p>
    <p><strong>绑定时间：</strong>{binding.bound_at}</p>
    <p><strong>验证状态：</strong>{"✅ 已验证" if binding.confirmed else "⏳ 待验证"}</p>
    """
    
    footer = f"查询时间：{event.time}"
    
    # 生成并渲染卡片
    html_content = html_render_service.create_card_style(
        title=title,
        content=content,
        footer=footer,
        theme="light"
    )
    
    image_bytes = await html_render_service.render_html(html_content)
    
    # 发送图片
    await usercard.send(MessageSegment.image(image_bytes))
```

## 示例 2：生成群组排行榜

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from services.html_render import html_render_service


leaderboard = on_command("leaderboard", priority=5)


@leaderboard.handle()
async def handle_leaderboard(bot: Bot, event: GroupMessageEvent):
    """生成活跃度排行榜"""
    
    # 模拟数据（实际应该从数据库获取）
    users = [
        {"rank": 1, "name": "用户A", "score": 9850},
        {"rank": 2, "name": "用户B", "score": 8720},
        {"rank": 3, "name": "用户C", "score": 7650},
        {"rank": 4, "name": "用户D", "score": 6540},
        {"rank": 5, "name": "用户E", "score": 5430},
    ]
    
    # 构建 Markdown 表格
    markdown = "# 🏆 活跃度排行榜\n\n"
    markdown += "| 排名 | 用户 | 分数 |\n"
    markdown += "|------|------|------|\n"
    
    for user in users:
        medal = ["🥇", "🥈", "🥉"][user["rank"]-1] if user["rank"] <= 3 else "🏅"
        markdown += f"| {medal} {user['rank']} | {user['name']} | {user['score']} |\n"
    
    markdown += "\n*数据更新于今天*"
    
    # 自定义 CSS
    custom_css = """
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    th {
        background-color: #3498db;
        color: white;
        padding: 12px;
        text-align: left;
    }
    td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    """
    
    # 渲染为图片
    image_bytes = await html_render_service.render_markdown(
        markdown_content=markdown,
        css=custom_css
    )
    
    await leaderboard.send(MessageSegment.image(image_bytes))
```

## 示例 3：生成活动公告

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from services.html_render import html_render_service
from datetime import datetime


announce = on_command("makeannounce", priority=5)


@announce.handle()
async def handle_announce(bot: Bot, event: GroupMessageEvent):
    """生成活动公告卡片"""
    
    title = "🎉 周末 VRChat 聚会活动"
    
    content = """
    <h3>📅 活动时间</h3>
    <p>本周六晚上 8:00 - 10:00 (UTC+8)</p>
    
    <h3>🌍 活动地点</h3>
    <p>世界名称：The Great Pug</p>
    <p>世界 ID：wrld_xxx</p>
    
    <h3>📋 活动内容</h3>
    <ul>
        <li>社交交流</li>
        <li>小游戏环节</li>
        <li>合影留念</li>
    </ul>
    
    <h3>⚠️ 注意事项</h3>
    <ul>
        <li>请提前 10 分钟进入世界</li>
        <li>遵守 VRChat 社区准则</li>
        <li>如有问题请联系管理员</li>
    </ul>
    """
    
    footer = f"发布时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 使用暗色主题
    html_content = html_render_service.create_card_style(
        title=title,
        content=content,
        footer=footer,
        theme="dark"
    )
    
    image_bytes = await html_render_service.render_html(html_content)
    
    await announce.send(MessageSegment.image(image_bytes))
```

## 示例 4：生成统计报告

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from services.html_render import html_render_service
from datetime import datetime


stats = on_command("stats", priority=5)


@stats.handle()
async def handle_stats(bot: Bot, event: GroupMessageEvent):
    """生成群组统计报告"""
    
    # 模拟统计数据
    total_members = 3975
    online_now = 128
    bound_users = 450
    today_joins = 12
    today_leaves = 3
    
    markdown = f"""# 📊 群组统计报告

## 基本数据

| 指标 | 数值 |
|------|------|
| 总成员数 | {total_members:,} |
| 当前在线 | {online_now} |
| 已绑定用户 | {bound_users} |
| 今日加入 | +{today_joins} |
| 今日离开 | -{today_leaves} |

## 趋势分析

**净增长**: +{today_joins - today_leaves} 人

**绑定率**: {bound_users/total_members*100:.1f}%

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    # 自定义样式
    custom_css = """
    .stat-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    """
    
    image_bytes = await html_render_service.render_markdown(
        markdown_content=markdown,
        css=custom_css
    )
    
    await stats.send(MessageSegment.image(image_bytes))
```

## 示例 5：使用 Jinja2 模板

首先创建模板文件 `templates/user_profile.html.jinja`：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: "Microsoft YaHei", sans-serif;
            padding: 20px;
            background-color: {{ bg_color }};
        }
        .profile-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background-color: #ddd;
            margin: 0 auto 20px;
        }
        .name {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .label {
            color: #666;
        }
        .value {
            color: #333;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="profile-card">
        <div class="avatar"></div>
        <div class="name">{{ display_name }}</div>
        
        <div class="info-row">
            <span class="label">用户 ID</span>
            <span class="value">{{ user_id }}</span>
        </div>
        
        <div class="info-row">
            <span class="label">等级</span>
            <span class="value">{{ trust_rank }}</span>
        </div>
        
        <div class="info-row">
            <span class="label">加入时间</span>
            <span class="value">{{ join_date }}</span>
        </div>
        
        {% if bio %}
        <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <strong>个人简介</strong>
            <p style="margin-top: 10px; color: #666;">{{ bio }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
```

然后在插件中使用：

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from services.html_render import html_render_service
from pathlib import Path


profile = on_command("profile", priority=5)


@profile.handle()
async def handle_profile(bot: Bot, event: GroupMessageEvent):
    """使用模板生成用户资料卡"""
    
    # 准备模板数据
    context = {
        "display_name": "测试用户",
        "user_id": "usr_xxx",
        "trust_rank": "Trusted",
        "join_date": "2024-01-01",
        "bio": "这是一个测试用户的个人简介",
        "bg_color": "#f0f4f8"
    }
    
    # 渲染模板
    template_path = Path("templates/user_profile.html.jinja")
    
    image_bytes = await html_render_service.render_template(
        template_path=template_path,
        context=context,
        width=600
    )
    
    await profile.send(MessageSegment.image(image_bytes))
```

## 示例 6：批量生成图片并缓存

```python
from services.html_render import html_render_service
from pathlib import Path
import hashlib


class ImageCache:
    """简单的图片缓存"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, content: str) -> str:
        """生成缓存键"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, content: str) -> bytes | None:
        """从缓存获取图片"""
        cache_key = self._get_cache_key(content)
        cache_file = self.cache_dir / f"{cache_key}.png"
        
        if cache_file.exists():
            return cache_file.read_bytes()
        return None
    
    def set(self, content: str, image_bytes: bytes):
        """保存图片到缓存"""
        cache_key = self._get_cache_key(content)
        cache_file = self.cache_dir / f"{cache_key}.png"
        cache_file.write_bytes(image_bytes)


# 使用示例
cache = ImageCache()


async def get_or_render_card(title: str, content: str) -> bytes:
    """获取或渲染卡片"""
    
    # 构建唯一标识
    cache_key = f"{title}:{content}"
    
    # 尝试从缓存获取
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # 渲染新图片
    html = html_render_service.create_card_style(
        title=title,
        content=content,
        theme="light"
    )
    
    image_bytes = await html_render_service.render_html(html)
    
    # 保存到缓存
    cache.set(cache_key, image_bytes)
    
    return image_bytes
```

## 最佳实践

### 1. 错误处理

```python
try:
    image_bytes = await html_render_service.render_markdown(content)
    await matcher.send(MessageSegment.image(image_bytes))
except Exception as e:
    logger.error(f"渲染失败: {e}")
    await matcher.send(f"❌ 生成图片失败: {str(e)}")
```

### 2. 性能优化

```python
# 控制图片尺寸
image_bytes = await html_render_service.render_markdown(
    content,
    width=800  # 不要太大
)

# 简化 CSS，避免复杂样式
simple_css = """
body { font-size: 16px; }
"""
```

### 3. 中文支持

确保系统安装了中文字体：
- Windows：通常自带 Microsoft YaHei
- Linux：安装 `fonts-wqy-zenhei` 或 `fonts-noto-cjk`

### 4. 调试技巧

```python
# 保存生成的 HTML 以便调试
html_content = html_render_service.create_card_style(...)
Path("debug.html").write_text(html_content, encoding="utf-8")

# 然后在浏览器中打开查看效果
```

## 常见问题

### Q: 如何调整字体大小？
A: 在 `render_text()` 中设置 `font_size` 参数，或在 CSS 中定义。

### Q: 支持哪些 CSS 属性？
A: litehtml 支持大部分标准 CSS，但不支持 JavaScript 和部分高级特性。

### Q: 如何添加图片？
A: 可以使用 base64 编码的图片，或提供可访问的 URL。

### Q: 渲染速度慢怎么办？
A: 
- 减小图片宽度
- 简化 HTML/CSS
- 使用缓存
- 首次加载会较慢（字体加载）

---

更多问题和示例，请参考 [HTML_RENDER_GUIDE.md](./HTML_RENDER_GUIDE.md)
