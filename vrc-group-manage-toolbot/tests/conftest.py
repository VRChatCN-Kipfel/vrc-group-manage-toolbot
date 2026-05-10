import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import nonebot
nonebot.init()

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Adapter
get_driver().register_adapter(Adapter)


@pytest.fixture(scope="session")
def nonebot_init():
    return nonebot


@pytest.fixture(scope="session")
def _cleanup_data_dir():
    data_dir = Path("data/vrc_toolbot")
    before: set[str] = set()
    if data_dir.exists():
        before = {f.name for f in data_dir.iterdir() if f.is_file()}

    yield

    if data_dir.exists():
        for f in data_dir.iterdir():
            if f.is_file() and f.name not in before and f.name.startswith("test_"):
                try:
                    f.unlink()
                except OSError:
                    pass


@pytest.fixture(autouse=True)
def _cleanup_temp_state():
    yield
    from services.permission import _temp_permissions
    from services.api_guard import api_guard
    _temp_permissions.clear()
    api_guard.clear_cache()
