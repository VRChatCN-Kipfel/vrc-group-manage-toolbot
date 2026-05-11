"""
测试运行脚本
提供便捷的测试执行命令
"""
import sys
import subprocess
from pathlib import Path


def run_tests(args=None):
    """运行测试"""
    cmd = ["pytest"]
    
    if args:
        cmd.extend(args)
    else:
        # 默认运行所有测试
        cmd.extend(["tests/", "-v"])
    
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    # 切换到项目根目录
    project_root = Path(__file__).parent
    sys.exit(run_tests(sys.argv[1:]))
