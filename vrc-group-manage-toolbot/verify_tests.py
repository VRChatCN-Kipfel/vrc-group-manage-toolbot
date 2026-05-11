"""
快速验证测试框架是否正常工作
"""
import subprocess
import sys


def main():
    print("=" * 60)
    print("VRChat Bot 测试框架验证")
    print("=" * 60)
    print()
    
    # 运行一个简单的测试来验证框架
    print("运行基础测试...")
    result = subprocess.run(
        ["pytest", "tests/services/__init__.py::TestGroupConfig::test_command_defaults_exist", "-v"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n✅ 测试框架工作正常！")
        print("\n接下来你可以：")
        print("  1. 运行所有测试: pytest tests/ -v")
        print("  2. 查看测试说明: cat tests/README.md")
        print("  3. 查看架构文档: cat TEST_ARCHITECTURE.md")
        return 0
    else:
        print("\n❌ 测试框架存在问题，请检查错误信息")
        print(result.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
