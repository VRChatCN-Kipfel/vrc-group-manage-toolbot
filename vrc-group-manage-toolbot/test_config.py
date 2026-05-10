"""
配置系统测试入口
使用方法: python test_config.py
委托到 pytest 运行 tests/ 目录下的完整测试套件
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["tests/", "-v"]))
