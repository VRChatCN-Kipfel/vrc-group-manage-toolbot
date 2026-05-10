"""
定时任务调度服务
基于 nonebot-plugin-apscheduler 提供统一的调度接口
"""

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler


class SchedulerService:
    """调度服务包装类"""

    @staticmethod
    def add_interval_task(
        func,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        task_id: str = None,
        **kwargs
    ):
        """添加周期性间隔任务"""
        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id or func.__name__,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"已注册间隔任务: {task_id or func.__name__} (每 {seconds}s {minutes}m {hours}h)")

    @staticmethod
    def add_cron_task(
        func,
        cron_expr: str,
        task_id: str = None,
        **kwargs
    ):
        """添加 Cron 表达式任务"""
        # 简单的 Cron 解析，实际可根据需求扩展
        parts = cron_expr.split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
            trigger = CronTrigger(
                minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
            )
            scheduler.add_job(
                func,
                trigger=trigger,
                id=task_id or func.__name__,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"已注册 Cron 任务: {task_id or func.__name__} ({cron_expr})")
        else:
            logger.error(f"Cron 表达式格式错误: {cron_expr}")

    @staticmethod
    def remove_task(task_id: str):
        """移除指定任务"""
        try:
            scheduler.remove_job(task_id)
            logger.info(f"已移除任务: {task_id}")
        except Exception as e:
            logger.warning(f"移除任务 {task_id} 失败: {e}")

    @staticmethod
    def get_all_jobs():
        """获取所有当前运行的任务"""
        return scheduler.get_jobs()


# 实例化服务，方便其他模块导入使用
scheduler_service = SchedulerService()
