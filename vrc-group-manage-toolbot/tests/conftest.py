"""
Pytest fixtures for services tests
Mock NoneBot dependencies before any imports to allow unit testing without runtime.
"""
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

TEST_ROOT = Path(__file__).parent
SRC_DIR = TEST_ROOT.parent
sys.path.insert(0, str(SRC_DIR))

MOCKED_MODULES = [
    "nonebot",
    "nonebot.adapters",
    "nonebot.adapters.onebot",
    "nonebot.adapters.onebot.v11",
    "nonebot.log",
    "nonebot.matcher",
    "nonebot.params",
    "nonebot.typing",
    "nonebot.plugin",
    "nonebot_plugin_localstore",
    "nonebot_plugin_apscheduler",
]

for mod_name in MOCKED_MODULES:
    if mod_name not in sys.modules:
        mock = MagicMock()
        mock.logger = MagicMock()
        sys.modules[mod_name] = mock

sys.modules["nonebot.log"].logger = MagicMock()
sys.modules["nonebot_plugin_apscheduler"].scheduler = MagicMock()
sys.modules["nonebot_plugin_apscheduler"].scheduler.running = False
sys.modules["nonebot_plugin_apscheduler"].scheduler.get_job = MagicMock(return_value=None)
sys.modules["nonebot_plugin_apscheduler"].scheduler.get_jobs = MagicMock(return_value=[])
sys.modules["nonebot_plugin_apscheduler"].scheduler.add_job = MagicMock()
sys.modules["nonebot_plugin_apscheduler"].scheduler.remove_job = MagicMock()


@pytest.fixture
def temp_config_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_scheduler():
    scheduler = MagicMock()
    scheduler.get_job.return_value = None
    scheduler.get_jobs.return_value = []
    scheduler.running = False
    return scheduler
