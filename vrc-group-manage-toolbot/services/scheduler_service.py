"""
定时任务调度服务
基于 nonebot-plugin-apscheduler 提供统一的调度接口
"""
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler as default_scheduler


class TaskAlreadyExistsError(Exception):
    """任务已存在异常"""
    def __init__(self, task_id: str, message: str = None):
        self.task_id = task_id
        self.message = message or f"任务 '{task_id}' 已存在"
        super().__init__(self.message)


class SchedulerService:
    """调度服务包装类"""

    def __init__(self, scheduler: BaseScheduler = None):
        self.scheduler = scheduler or default_scheduler

    def add_interval_task(
        self,
        func,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        task_id: str = None,
        force_replace: bool = False,
        **kwargs
    ):
        task_id = task_id or func.__name__

        existing_job = self.scheduler.get_job(task_id)
        if existing_job:
            if not force_replace:
                logger.warning(f"任务 {task_id} 已存在，拒绝注册（如需覆盖请设置 force_replace=True）")
                raise TaskAlreadyExistsError(task_id)
            else:
                logger.info(f"任务 {task_id} 已存在，将强制覆盖")

        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"已注册间隔任务: {task_id} (每 {seconds}s {minutes}m {hours}h)")

    def add_cron_task(
        self,
        func,
        cron_expr: str,
        task_id: str = None,
        force_replace: bool = False,
        **kwargs
    ):
        task_id = task_id or func.__name__
        try:
            existing_job = self.scheduler.get_job(task_id)
            if existing_job:
                if not force_replace:
                    logger.warning(f"任务 {task_id} 已存在，拒绝注册（如需覆盖请设置 force_replace=True）")
                    raise TaskAlreadyExistsError(task_id)
                else:
                    logger.info(f"任务 {task_id} 已存在，将强制覆盖")

            trigger = CronTrigger.from_crontab(cron_expr)
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=task_id,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"已注册 Cron 任务: {task_id} ({cron_expr})")
        except TaskAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Cron 表达式格式错误或注册失败: {cron_expr}, 错误: {e}")
            raise

    def remove_task(self, task_id: str):
        try:
            self.scheduler.remove_job(task_id)
            logger.info(f"已移除任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def get_all_jobs(self):
        return self.scheduler.get_jobs()

    def get_task_info(self, task_id: str):
        job = self.scheduler.get_job(task_id)
        if job:
            func_name = job.func_ref or getattr(job.func, '__name__', repr(job.func))
            return {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': str(job.next_run_time),
                'func': func_name
            }
        return None

    def pause_task(self, task_id: str):
        try:
            self.scheduler.pause_job(task_id)
            logger.info(f"已暂停任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def resume_task(self, task_id: str):
        try:
            self.scheduler.resume_job(task_id)
            logger.info(f"已恢复任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def modify_task(self, task_id: str, **changes):
        try:
            self.scheduler.modify_job(task_id, **changes)
            logger.info(f"已修改任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def add_date_task(self, func, run_date, task_id: str = None, force_replace: bool = False, **kwargs):
        task_id = task_id or func.__name__

        existing_job = self.scheduler.get_job(task_id)
        if existing_job:
            if not force_replace:
                logger.warning(f"任务 {task_id} 已存在，拒绝注册（如需覆盖请设置 force_replace=True）")
                raise TaskAlreadyExistsError(task_id)
            else:
                logger.info(f"任务 {task_id} 已存在，将强制覆盖")

        trigger = DateTrigger(run_date=run_date)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"已注册一次性任务: {task_id} (运行时间: {run_date})")

    def is_scheduler_running(self):
        return self.scheduler.running

    def start_scheduler(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("调度器已手动启动")
        else:
            logger.warning("调度器已在运行中")

    def shutdown_scheduler(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("调度器已手动关闭")
        else:
            logger.warning("调度器未运行")


scheduler_service = SchedulerService()
