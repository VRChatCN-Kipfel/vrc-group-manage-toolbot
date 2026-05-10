"""
定时任务演示插件
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from services.scheduler_service import scheduler_service
from services.permission import get_permission_level, PermissionLevel


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
