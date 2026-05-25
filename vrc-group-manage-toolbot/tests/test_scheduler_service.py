"""
Unit tests for SchedulerService core API
"""
from unittest.mock import MagicMock

import pytest

from services.scheduler_service import SchedulerService, TaskAlreadyExistsError


@pytest.fixture
def svc_with_mock(mock_scheduler):
    return SchedulerService(scheduler=mock_scheduler)


class TestSchedulerServiceCore:
    """调度服务核心 API 测试"""

    def test_add_interval_task_with_force_replace(self, svc_with_mock):
        svc_with_mock.scheduler.get_job.return_value = MagicMock()

        async def task():
            pass

        svc_with_mock.add_interval_task(
            func=task, seconds=10, task_id="test_task", force_replace=True,
        )
        svc_with_mock.scheduler.add_job.assert_called_once()

    def test_add_interval_task_duplicate_raises(self, svc_with_mock):
        svc_with_mock.scheduler.get_job.return_value = MagicMock()

        async def task():
            pass

        with pytest.raises(TaskAlreadyExistsError):
            svc_with_mock.add_interval_task(
                func=task, seconds=10, task_id="test_task",
            )

    def test_remove_task_raises_job_lookup_error(self, svc_with_mock):
        from apscheduler.jobstores.base import JobLookupError
        svc_with_mock.scheduler.remove_job.side_effect = JobLookupError("not found")

        with pytest.raises(JobLookupError):
            svc_with_mock.remove_task("nonexistent")

    def test_get_task_info_returns_none_for_missing(self, svc_with_mock):
        svc_with_mock.scheduler.get_job.return_value = None
        assert svc_with_mock.get_task_info("missing") is None

    def test_no_managed_task_registry(self, svc_with_mock):
        """确保不再有 ManagedTaskRegistry"""
        assert not hasattr(svc_with_mock, '_managed_tasks')
        assert not hasattr(svc_with_mock, 'register_managed_task')
        assert not hasattr(svc_with_mock, 'reload_managed_tasks')
