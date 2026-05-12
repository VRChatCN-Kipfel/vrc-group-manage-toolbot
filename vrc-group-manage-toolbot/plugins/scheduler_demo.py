"""
定时任务演示插件
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from services.scheduler_service import scheduler_service
from services.permission import get_permission_level, PermissionLevel
import asyncio
from datetime import datetime, timedelta


# 定义一个要周期性执行的任务函数
async def demo_periodic_task():
    """这是一个每 10 秒执行一次的演示任务"""
    logger.info("🕒 定时任务触发: 正在执行演示任务...")
    # 在这里可以放置你的业务逻辑，比如检查 API 状态、清理缓存等


# 注册间隔任务：每 10 秒执行一次
scheduler_service.add_interval_task(
    func=demo_periodic_task,
    seconds=10,
    task_id="demo_task_10s"
)


# 定义一个 Cron 任务函数
async def demo_cron_task():
    """这是一个每天凌晨执行的演示任务"""
    logger.info("🌅 Cron 定时任务触发: 正在执行每日清理任务...")
    # 模拟一些清理工作
    await asyncio.sleep(1)
    logger.info("✅ 每日清理任务完成")


# 注册 Cron 任务：每天凌晨 2:30 执行
scheduler_service.add_cron_task(
    func=demo_cron_task,
    cron_expr="30 2 * * *",  # 分 时 日 月 星期
    task_id="demo_cron_daily"
)


# 定义一个一次性任务函数
async def demo_one_time_task():
    """这是一个一次性执行的演示任务"""
    logger.info("⏰ 一次性任务触发: 执行特定时间的任务")
    await asyncio.sleep(1)
    logger.info("✅ 一次性任务完成")


# 注册一次性任务：5分钟后执行（仅作为示例，实际使用时可根据需要设置时间）
# 注意：由于这个是在模块加载时就注册的，所以每次重启都会重新设置
run_time = datetime.now() + timedelta(minutes=5)
scheduler_service.add_date_task(
    func=demo_one_time_task,
    run_date=run_time,
    task_id="demo_one_time_task"
)


# 创建一个命令来查看当前所有任务
show_tasks = on_command("tasks", priority=5)


@show_tasks.handle()
async def handle_show_tasks(bot: Bot, event: MessageEvent):
    # 仅限超级管理员查看
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await show_tasks.finish("❌ 仅超级管理员可查看任务列表")

    jobs = scheduler_service.get_all_jobs()
    
    if not jobs:
        await show_tasks.finish("✨ 当前没有运行中的定时任务")

    msg = "📋 当前运行的定时任务:\n" + "=" * 30 + "\n"
    for job in jobs:
        msg += f"ID: {job.id}\n"
        msg += f"下次执行: {job.next_run_time}\n"
        msg += "-" * 20 + "\n"

    await show_tasks.finish(msg)


# 查看任务详细信息命令
task_info = on_command("task_info", priority=5)


@task_info.handle()
async def handle_task_info(bot: Bot, event: MessageEvent):
    # 仅限超级管理员查看
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await task_info.finish("❌ 仅超级管理员可查看任务信息")

    # 从消息中获取任务ID
    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await task_info.finish("❌ 请提供任务ID，例如: /task_info demo_task_10s")
    
    task_id = args[1]
    info = scheduler_service.get_task_info(task_id)
    
    if info:
        msg = f"📊 任务信息:\n"
        msg += f"ID: {info['id']}\n"
        msg += f"名称: {info['name']}\n"
        msg += f"触发器: {info['trigger']}\n"
        msg += f"下次执行: {info['next_run_time']}\n"
        msg += f"函数: {info['func']}\n"
        await task_info.finish(msg)
    else:
        await task_info.finish(f"❌ 未找到任务: {task_id}")


# 暂停任务命令
pause_task_cmd = on_command("pause_task", priority=5)


@pause_task_cmd.handle()
async def handle_pause_task(bot: Bot, event: MessageEvent):
    # 仅限超级管理员操作
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await pause_task_cmd.finish("❌ 仅超级管理员可暂停任务")

    # 从消息中获取任务ID
    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await pause_task_cmd.finish("❌ 请提供任务ID，例如: /pause_task demo_task_10s")
    
    task_id = args[1]
    scheduler_service.pause_task(task_id)
    await pause_task_cmd.finish(f"⏸️ 已尝试暂停任务: {task_id}")


# 恢复任务命令
resume_task_cmd = on_command("resume_task", priority=5)


@resume_task_cmd.handle()
async def handle_resume_task(bot: Bot, event: MessageEvent):
    # 仅限超级管理员操作
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await resume_task_cmd.finish("❌ 仅超级管理员可恢复任务")

    # 从消息中获取任务ID
    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await resume_task_cmd.finish("❌ 请提供任务ID，例如: /resume_task demo_task_10s")
    
    task_id = args[1]
    scheduler_service.resume_task(task_id)
    await resume_task_cmd.finish(f"▶️ 已尝试恢复任务: {task_id}")


# 移除任务命令
remove_task_cmd = on_command("remove_task", priority=5)


@remove_task_cmd.handle()
async def handle_remove_task(bot: Bot, event: MessageEvent):
    # 仅限超级管理员操作
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await remove_task_cmd.finish("❌ 仅超级管理员可移除任务")

    # 从消息中获取任务ID
    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await remove_task_cmd.finish("❌ 请提供任务ID，例如: /remove_task demo_task_10s")
    
    task_id = args[1]
    scheduler_service.remove_task(task_id)
    await remove_task_cmd.finish(f"🗑️ 已尝试移除任务: {task_id}")


# 检查调度器状态命令
scheduler_status = on_command("scheduler_status", priority=5)


@scheduler_status.handle()
async def handle_scheduler_status(bot: Bot, event: MessageEvent):
    # 仅限超级管理员查看
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await scheduler_status.finish("❌ 仅超级管理员可查看调度器状态")

    is_running = scheduler_service.is_scheduler_running()
    status = "🟢 运行中" if is_running else "🔴 已停止"
    await scheduler_status.finish(f"调度器状态: {status}")
