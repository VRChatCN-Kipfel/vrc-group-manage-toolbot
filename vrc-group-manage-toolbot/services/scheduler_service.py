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


class SchedulerService:
    """调度服务包装类"""

    def __init__(self, scheduler: BaseScheduler = None):
        """
        初始化调度服务
        
        Args:
            scheduler: APScheduler 实例，默认为全局 scheduler
        """
        self.scheduler = scheduler or default_scheduler

    def add_interval_task(
        self,
        func,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        task_id: str = None,
        **kwargs
    ):
        """添加周期性间隔任务"""
        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id or func.__name__,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"已注册间隔任务: {task_id or func.__name__} (每 {seconds}s {minutes}m {hours}h)")

    def add_cron_task(
        self,
        func,
        cron_expr: str,
        task_id: str = None,
        **kwargs
    ):
        """添加 Cron 表达式任务"""
        try:
            trigger = CronTrigger.from_crontab(cron_expr)
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=task_id or func.__name__,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"已注册 Cron 任务: {task_id or func.__name__} ({cron_expr})")
        except Exception as e:
            logger.error(f"Cron 表达式格式错误或注册失败: {cron_expr}, 错误: {e}")

    def remove_task(self, task_id: str):
        """移除指定任务
        
        Raises:
            JobLookupError: 当任务不存在时抛出
        """
        try:
            self.scheduler.remove_job(task_id)
            logger.info(f"已移除任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def get_all_jobs(self):
        """获取所有当前运行的任务"""
        return self.scheduler.get_jobs()

    def get_task_info(self, task_id: str):
        """获取指定任务的详细信息"""
        job = self.scheduler.get_job(task_id)
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': str(job.next_run_time),
                'func': job.func_ref or str(job.func)
            }
        return None

    def pause_task(self, task_id: str):
        """暂停指定任务
        
        Raises:
            JobLookupError: 当任务不存在时抛出
        """
        try:
            self.scheduler.pause_job(task_id)
            logger.info(f"已暂停任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def resume_task(self, task_id: str):
        """恢复指定任务
        
        Raises:
            JobLookupError: 当任务不存在时抛出
        """
        try:
            self.scheduler.resume_job(task_id)
            logger.info(f"已恢复任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def modify_task(self, task_id: str, **changes):
        """修改任务参数
        
        Raises:
            JobLookupError: 当任务不存在时抛出
        """
        try:
            self.scheduler.modify_job(task_id, **changes)
            logger.info(f"已修改任务: {task_id}")
        except JobLookupError:
            logger.warning(f"任务不存在: {task_id}")
            raise

    def add_date_task(self, func, run_date, task_id: str = None, **kwargs):
        """添加一次性定时任务"""
        trigger = DateTrigger(run_date=run_date)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id or func.__name__,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"已注册一次性任务: {task_id or func.__name__} (运行时间: {run_date})")

    def is_scheduler_running(self):
        """检查调度器是否正在运行"""
        return self.scheduler.running

    def start_scheduler(self):
        """手动启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("调度器已手动启动")
        else:
            logger.warning("调度器已在运行中")

    def shutdown_scheduler(self):
        """手动关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("调度器已手动关闭")
        else:
            logger.warning("调度器未运行")


# 实例化服务，方便其他模块导入使用
scheduler_service = SchedulerService()
