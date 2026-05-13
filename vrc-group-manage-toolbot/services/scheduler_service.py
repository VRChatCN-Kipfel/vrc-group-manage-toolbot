"""
定时任务调度服务
基于 nonebot-plugin-apscheduler 提供统一的调度接口
"""

from nonebot import require

# 加载 nonebot_plugin_apscheduler 插件
require("nonebot_plugin_apscheduler")

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
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
        try:
            trigger = CronTrigger.from_crontab(cron_expr)
            scheduler.add_job(
                func,
                trigger=trigger,
                id=task_id or func.__name__,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"已注册 Cron 任务: {task_id or func.__name__} ({cron_expr})")
        except Exception as e:
            logger.error(f"Cron 表达式格式错误或注册失败: {cron_expr}, 错误: {e}")

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

    @staticmethod
    def get_task_info(task_id: str):
        """获取指定任务的详细信息"""
        job = scheduler.get_job(task_id)
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': str(job.next_run_time),
                'func': job.func_ref or str(job.func)
            }
        return None

    @staticmethod
    def pause_task(task_id: str):
        """暂停指定任务"""
        try:
            scheduler.pause_job(task_id)
            logger.info(f"已暂停任务: {task_id}")
        except Exception as e:
            logger.warning(f"暂停任务 {task_id} 失败: {e}")

    @staticmethod
    def resume_task(task_id: str):
        """恢复指定任务"""
        try:
            scheduler.resume_job(task_id)
            logger.info(f"已恢复任务: {task_id}")
        except Exception as e:
            logger.warning(f"恢复任务 {task_id} 失败: {e}")

    @staticmethod
    def modify_task(task_id: str, **changes):
        """修改任务参数"""
        try:
            scheduler.modify_job(task_id, **changes)
            logger.info(f"已修改任务: {task_id}")
        except Exception as e:
            logger.warning(f"修改任务 {task_id} 失败: {e}")

    @staticmethod
    def add_date_task(func, run_date, task_id: str = None, **kwargs):
        """添加一次性定时任务"""
        trigger = DateTrigger(run_date=run_date)
        scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id or func.__name__,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"已注册一次性任务: {task_id or func.__name__} (运行时间: {run_date})")

    @staticmethod
    def is_scheduler_running():
        """检查调度器是否正在运行"""
        return scheduler.running

    @staticmethod
    def start_scheduler():
        """手动启动调度器"""
        if not scheduler.running:
            scheduler.start()
            logger.info("调度器已手动启动")
        else:
            logger.warning("调度器已在运行中")

    @staticmethod
    def shutdown_scheduler():
        """手动关闭调度器"""
        if scheduler.running:
            scheduler.shutdown()
            logger.info("调度器已手动关闭")
        else:
            logger.warning("调度器未运行")


# 实例化服务，方便其他模块导入使用
scheduler_service = SchedulerService()
