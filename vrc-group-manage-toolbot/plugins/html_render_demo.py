"""
HTML 渲染示例插件
演示如何使用 html_render_service 进行图片渲染
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
    - #htmldemo text - 演示文本渲染
    - #htmldemo md - 演示 Markdown 渲染
    - #htmldemo card - 演示卡片渲染
    - #htmldemo dark - 演示暗色主题卡片
    """
    text = args.extract_plain_text().strip()
    
    if not text or text == "text":
        # 演示纯文本渲染
        await demo_text_rendering(event)
    elif text == "md":
        # 演示 Markdown 渲染
        await demo_markdown_rendering(event)
    elif text == "card":
        # 演示亮色主题卡片
        await demo_card_rendering(event, theme="light")
    elif text == "dark":
        # 演示暗色主题卡片
        await demo_card_rendering(event, theme="dark")
    else:
        await html_demo.finish("❌ 未知参数\n用法：\n- #htmldemo text - 文本渲染\n- #htmldemo md - Markdown 渲染\n- #htmldemo card - 亮色卡片\n- #htmldemo dark - 暗色卡片")


async def demo_text_rendering(event: GroupMessageEvent):
    """演示纯文本渲染"""
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
        
        image_bytes = await html_render_service.render_text(
            text=text_content,
            font_size=16,
            width=800,
            padding=20,
            bg_color="#f0f4f8",
            text_color="#2c3e50"
        )
        
        # 发送图片
        await html_demo.send(MessageSegment.image(image_bytes))
        await html_demo.send("✅ 文本渲染演示完成")
        
    except Exception as e:
        logger.error(f"文本渲染演示失败: {e}")
        await html_demo.finish(f"❌ 渲染失败: {str(e)}")


async def demo_markdown_rendering(event: GroupMessageEvent):
    """演示 Markdown 渲染"""
    try:
        markdown_content = """# VRChat 群组管理系统

## 📋 功能特性

### 查询功能
- **instances** - 查询群组活跃实例
- **whereis** - 查询用户位置
- **whois** - 查询用户详细信息

### 管理功能
- **gmembers** - 查看群组成员列表
- **grole** - 管理成员角色
- **grequests** - 处理加入申请

### 用户绑定
- **bind** - 绑定 VRChat 账号
- **unbind** - 解除绑定
- **bindinfo** - 查看绑定信息

## 🔧 技术栈

| 组件 | 版本 |
|------|------|
| NoneBot2 | >=2.5.0 |
| OneBot V11 | >=2.4.6 |
| Python | >=3.10 |

## 💡 使用提示

> 使用前请先绑定您的 VRChat 账号
> 部分命令需要特定权限等级

*最后更新：2026-05-10*"""
        
        image_bytes = await html_render_service.render_markdown(
            markdown_content=markdown_content,
            width=800
        )
        
        # 发送图片
        await html_demo.send(MessageSegment.image(image_bytes))
        await html_demo.send("✅ Markdown 渲染演示完成")
        
    except Exception as e:
        logger.error(f"Markdown 渲染演示失败: {e}")
        await html_demo.finish(f"❌ 渲染失败: {str(e)}")


async def demo_card_rendering(event: GroupMessageEvent, theme: str = "light"):
    """演示卡片渲染"""
    try:
        title = "🎮 VRChat 群组信息"
        
        content = """
<p><strong>群组名称：</strong>中文 Kipfel 厅</p>
<p><strong>群组 ID：</strong>grp_fdd4cdf6-b3e0-4be3-a040-5b8abf2617f4</p>
<p><strong>成员数量：</strong>3,975 人</p>
<p><strong>在线人数：</strong>128 人</p>
<p><strong>活跃实例：</strong>5 个</p>
<hr>
<p><strong>当前状态：</strong>🟢 正常运行</p>
<p><strong>最后更新：</strong>2026-05-10 12:00:00</p>
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
        
        # 发送图片
        await html_demo.send(MessageSegment.image(image_bytes))
        await html_demo.send(f"✅ {theme.title()} 主题卡片渲染演示完成")
        
    except Exception as e:
        logger.error(f"卡片渲染演示失败: {e}")
        await html_demo.finish(f"❌ 渲染失败: {str(e)}")


# 另一个示例：动态生成群组状态卡片
group_status = on_command("groupstatus", aliases={"群组状态"}, priority=5)


@group_status.handle()
async def handle_group_status(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    显示当前群组的 VRChat 群组状态卡片
    """
    from services.group_config import group_config_store
    
    # 获取当前群绑定的 VRChat 群组
    config = group_config_store.get(str(event.group_id))
    
    if not config.default_vrc_group:
        await group_status.finish("❌ 当前群未绑定 VRChat 群组\n请使用 #bindgroup grp_xxx 进行绑定")
    
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
            theme="light",
            width=800
        )
        
        await group_status.send(MessageSegment.image(image_bytes))
        
    except Exception as e:
        logger.error(f"群组状态卡片生成失败: {e}")
        await group_status.finish(f"❌ 生成失败: {str(e)}")


# 帮助命令
html_help = on_command("htmlhelp", aliases={"渲染帮助"}, priority=5)


@html_help.handle()
async def handle_html_help(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """显示 HTML 渲染功能的帮助信息"""
    
    help_md = """# 🎨 HTML 渲染功能帮助

## 可用命令

### #htmldemo [类型]
HTML 渲染演示命令

**参数：**
- `text` - 演示纯文本渲染
- `md` - 演示 Markdown 渲染
- `card` - 演示亮色主题卡片
- `dark` - 演示暗色主题卡片

**示例：**
```
#htmldemo text
#htmldemo md
#htmldemo card
#htmldemo dark
```

### #groupstatus
显示当前群的 VRChat 群组状态卡片

## 功能说明

本插件基于 `nonebot-plugin-htmlkit` 提供：
- ✅ 纯文本转图片
- ✅ Markdown 转图片
- ✅ HTML 转图片
- ✅ Jinja2 模板渲染
- ✅ 自定义 CSS 样式
- ✅ 多种主题支持

## 技术细节

- 渲染引擎：litehtml
- 字体管理：fontconfig
- 输出格式：PNG
- 默认宽度：800px

---
*更多功能正在开发中...*"""
    
    try:
        image_bytes = await html_render_service.render_markdown(
            markdown_content=help_md,
            width=800
        )
        
        await html_help.send(MessageSegment.image(image_bytes))
        
    except Exception as e:
        logger.error(f"帮助信息渲染失败: {e}")
        # 降级为文本发送
        await html_help.send(help_md)
