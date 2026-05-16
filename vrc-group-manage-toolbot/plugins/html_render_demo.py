"""
HTML 渲染示例插件（演示用）

⚠️ 注意：此插件仅用于演示 html_render_service 的功能
生产环境中请根据实际需求编写自己的插件

功能演示：
- 纯文本渲染为图片
- Markdown 渲染为图片
- HTML 卡片渲染（支持多主题）
- 动态内容渲染
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg

from services.html_render import html_render_service


# 创建命令处理器
html_demo = on_command("htmldemo", aliases={"html测试"}, priority=5)


@html_demo.handle()
async def handle_html_demo(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    HTML 渲染演示命令
    
    用法：
    - #htmldemo text        - 演示纯文本渲染
    - #htmldemo md          - 演示 Markdown 渲染
    - #htmldemo card        - 演示亮色主题卡片
    - #htmldemo dark        - 演示暗色主题卡片
    - #htmldemo ocean       - 演示海洋蓝主题
    - #htmldemo rose        - 演示玫瑰粉主题
    - #htmldemo amber       - 演示琥珀金主题
    """
    text = args.extract_plain_text().strip().lower()
    
    if not text or text == "text":
        await demo_text_rendering(event)
    elif text == "md":
        await demo_markdown_rendering(event)
    elif text in ("card", "light"):
        await demo_card_rendering(event, theme="miku")
    elif text == "dark":
        await demo_card_rendering(event, theme="dark")
    elif text == "ocean":
        await demo_card_rendering(event, theme="ocean")
    elif text == "rose":
        await demo_card_rendering(event, theme="rose")
    elif text == "amber":
        await demo_card_rendering(event, theme="amber")
    elif text == "lavender":
        await demo_card_rendering(event, theme="lavender")
    else:
        help_msg = (
            "🎨 HTML 渲染演示命令\n"
            "━━━━━━━━━━━━━━━\n"
            "可用参数：\n"
            "• text   - 纯文本渲染\n"
            "• md     - Markdown 渲染\n"
            "• card   - 初音未来主题卡片\n"
            "• dark   - 深色主题卡片\n"
            "• ocean  - 海洋蓝主题\n"
            "• rose   - 玫瑰粉主题\n"
            "• amber  - 琥珀金主题\n"
            "• lavender - 薰衣草紫主题\n"
            "━━━━━━━━━━━━━━━\n"
            "示例：#htmldemo ocean"
        )
        await html_demo.finish(help_msg)


async def demo_text_rendering(event: GroupMessageEvent):
    """演示纯文本渲染（支持自定义样式）"""
    try:
        text_content = """VRChat 群组管理机器人

这是一个基于 NoneBot2 的 VRChat 群组管理工具。

主要功能：
• 查询群组实例信息
• 管理群组成员和角色
• 用户账号绑定
• 发布公告和审核申请

当前版本：v0.2.0
开发状态：活跃开发中"""
        
        # 渲染文本为图片（使用自定义样式）
        image_bytes = await html_render_service.render_text(
            text=text_content,
            width=800,
            theme="miku",  # 使用预设主题
            font_size=16,
            padding=40
        )
        
        # 发送图片并 @ 用户
        await html_demo.send(
            Message([MessageSegment.at(event.user_id), MessageSegment.text("\n")]),
            reply_message=True
        )
        await html_demo.send(MessageSegment.image(image_bytes))
        await html_demo.finish("✅ 文本渲染演示完成")
        
    except Exception as e:
        logger.error(f"文本渲染演示失败: {e}")
        await html_demo.finish(f"❌ 渲染失败: {str(e)}")


async def demo_markdown_rendering(event: GroupMessageEvent):
    """演示 Markdown 渲染（支持表格、代码块及图片）"""
    try:
        # Markdown 中嵌入图片语法: ![alt](url)
        cover_url = "https://api.vrchat.cloud/api/1/file/file_f9c7a3c5-6f5e-4975-9878-356199e3785f/6/file"
        
        # 使用 event 获取当前用户信息，使演示更具交互性
        user_name = event.sender.nickname or f"用户{event.user_id}"
        
        markdown_content = f"""# 🎮 VRChat 群组管理系统

![World Cover]({cover_url})

## 👋 欢迎, {user_name}

### 🔍 查询功能
- **instances** - 查询群组活跃实例
- **whereis** - 查询用户位置
- **whois** - 查询用户详细信息

### ⚙️ 管理功能
- **gmembers** - 查看群组成员列表
- **grole** - 管理成员角色
- **grequests** - 处理加入申请

### 👤 用户绑定
- **bind** - 绑定 VRChat 账号
- **unbind** - 解除绑定
- **bindinfo** - 查看绑定信息

## 🛠️ 技术栈

| 组件 | 版本要求 |
|------|----------|
| NoneBot2 | >=2.5.0 |
| OneBot V11 | >=2.4.6 |
| Python | >=3.10 |

## 💡 使用提示

> ⚠️ 使用前请先绑定您的 VRChat 账号
> 🔒 部分命令需要特定权限等级

*测试时间：{event.time}*"""
        
        # 渲染 Markdown 为图片
        image_bytes = await html_render_service.render_markdown(
            markdown_content=markdown_content,
            width=800,
            theme="miku"
        )
        
        # 发送图片
        await html_demo.send(MessageSegment.image(image_bytes))
        await html_demo.finish("✅ Markdown 渲染演示完成")
        
    except Exception as e:
        logger.error(f"Markdown 渲染演示失败: {e}")
        await html_demo.finish(f"❌ 渲染失败: {str(e)}")


async def demo_card_rendering(event: GroupMessageEvent, theme: str = "miku"):
    """演示卡片渲染（支持多种主题及外部图片，但是要注意限宽限高）"""
    try:
        title = "🎮 VRChat 群组信息"
        
        # 模拟一个 VRChat 房间 封面 URL
        cover_url = "https://api.vrchat.cloud/api/1/file/file_f9c7a3c5-6f5e-4975-9878-356199e3785f/6/file"
        
        # 使用 event 获取当前群号
        group_id = event.group_id
        
        content = f"""
<div style="text-align: center; margin-bottom: 15px;">
    <img src="{cover_url}" alt="World Cover" style="width: 200px; height: 200px; object-fit: cover; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
</div>
<p><strong>群组名称：</strong>中文 Kipfel 厅</p>
<p><strong>群组 ID：</strong>grp_fdd4cdf6-b3e0-4be3-a040-5b8abf2617f4</p>
<p><strong>成员数量：</strong>3,975 人</p>
<p><strong>在线人数：</strong>128 人</p>
<p><strong>活跃实例：</strong>5 个</p>
<hr>
<p><strong>当前状态：</strong>🟢 正常运行</p>
<p><strong>查询群号：</strong>{group_id}</p>
"""
        
        footer = f"由 VRChat Bot 生成 | 主题：{theme}"
        
        # 渲染卡片为图片
        image_bytes = await html_render_service.render_card(
            title=title,
            content=content,
            footer=footer,
            theme=theme,
            width=800
        )
        
        # 发送图片并结束
        await html_demo.send(MessageSegment.image(image_bytes))
        await html_demo.finish(f"✅ {theme.upper()} 主题卡片渲染完成")
        
    except Exception as e:
        logger.error(f"卡片渲染演示失败: {e}")
        await html_demo.finish(f"❌ 渲染失败: {str(e)}")


# 另一个示例：动态生成群组状态卡片
group_status = on_command("groupstatus", aliases={"群组状态"}, priority=5)


@group_status.handle()
async def handle_group_status(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    显示当前群组的 VRChat 群组状态卡片
    
    用法：#groupstatus
    """
    from services.group_config import group_config_store
    
    # 获取当前群绑定的 VRChat 群组
    config = group_config_store.get(str(event.group_id))
    
    if not config or not config.default_vrc_group:
        await group_status.finish(
            "❌ 当前群未绑定 VRChat 群组\n"
            "请使用 #bindgroup grp_xxx 进行绑定"
        )
    
    try:
        # 这里可以调用 VRC API 获取实时数据
        # 为了演示，我们使用模拟数据
        group_name = "中文 Kipfel 厅"
        group_id = config.default_vrc_group
        member_count = "3,975"
        online_count = "128"  # 实际应该从 API 获取
        
        title = f"📊 {group_name}"
        
        content = f"""
<p><strong>群组 ID：</strong>{group_id}</p>
<p><strong>成员总数：</strong>{member_count} 人</p>
<p><strong>当前在线：</strong>{online_count} 人</p>
<p><strong>绑定时间：</strong>{config.bound_at.strftime('%Y-%m-%d') if hasattr(config, 'bound_at') and config.bound_at else '未知'}</p>
<hr>
<p>💡 使用 <code>#instances</code> 查看活跃实例</p>
<p>💡 使用 <code>#gmembers</code> 查看成员列表</p>
"""
        
        footer = f"QQ群：{event.group_id} | 更新于 {event.time}"
        
        # 渲染卡片为图片
        image_bytes = await html_render_service.render_card(
            title=title,
            content=content,
            footer=footer,
            theme="miku",
            width=800
        )
        
        await group_status.finish(MessageSegment.image(image_bytes))
        
    except Exception as e:
        logger.error(f"群组状态卡片生成失败: {e}")
        await group_status.finish(f"❌ 生成失败: {str(e)}")


# 帮助命令
html_help = on_command("htmlhelp", aliases={"渲染帮助"}, priority=5)


@html_help.handle()
async def handle_html_help(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """显示 HTML 渲染功能的帮助信息"""
    
    help_md = """# 🎨 HTML 渲染功能帮助

## 📌 可用命令

### #htmldemo [类型]
HTML 渲染演示命令

**参数：**
- `text` - 演示纯文本渲染
- `md` - 演示 Markdown 渲染
- `card` - 演示初音未来主题卡片
- `dark` - 演示深色主题卡片
- `ocean` / `rose` / `amber` / `lavender` - 其他主题

**示例：**
```bash
#htmldemo text
#htmldemo md
#htmldemo ocean
```

### #groupstatus
显示当前群的 VRChat 群组状态卡片

---

## ✨ 功能说明

本插件基于 `nonebot-plugin-htmlkit` 提供：
- ✅ 纯文本转图片
- ✅ Markdown 转图片
- ✅ HTML 转图片
- ✅ Jinja2 模板渲染
- ✅ 自定义 CSS 样式
- ✅ 多种主题支持（miku/dark/ocean/rose/amber/lavender）

## 🔧 技术细节

- **渲染引擎**：litehtml
- **字体管理**：fontconfig
- **输出格式**：PNG
- **默认宽度**：800px

---
*💡 提示：此插件仅用于演示，生产环境请根据需求自行开发*"""
    
    try:
        image_bytes = await html_render_service.render_markdown(
            markdown_content=help_md,
            width=800,
            theme="miku"
        )
        
        await html_help.finish(MessageSegment.image(image_bytes))
        
    except Exception as e:
        logger.error(f"帮助信息渲染失败: {e}")
        # 降级为文本发送
        await html_help.finish(help_md)
