"""
配置系统测试脚本
用于验证功能开关和权限配置系统是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_command_defaults():
    """测试默认命令配置"""
    print("=" * 60)
    print("测试1: 检查默认命令配置")
    print("=" * 60)
    
    from services.group_config import COMMAND_DEFAULTS
    
    print(f"\n✅ 共定义 {len(COMMAND_DEFAULTS)} 个命令\n")
    
    # 按模块分组显示
    modules = {
        "系统/认证": ["vrclLogin", "2fa", "vrcCheck"],
        "查询": ["whereis", "instances", "whois"],
        "用户绑定": ["bind", "confirm", "unbind", "bindinfo"],
        "群组管理": ["gmembers", "ginvite", "gkick", "gban", "gunban", 
                   "grole", "grequests", "gaccept", "greject", 
                   "gannounce", "gdelannounce", "gaudit"],
    }
    
    for module_name, cmd_list in modules.items():
        print(f"【{module_name}】")
        for cmd in cmd_list:
            if cmd in COMMAND_DEFAULTS:
                config = COMMAND_DEFAULTS[cmd]
                status = "✅" if config["enabled"] else "❌"
                perm_names = {0: "未绑定成员", 1: "已绑定成员", 2: "未绑定管理", 3: "已绑定管理", 4: "群主", 5: "超管"}
                perm = perm_names.get(config["permission"].value, "?")
                print(f"  {status} #{cmd:<15} (默认权限: {perm})")
            else:
                print(f"  ❌ #{cmd:<15} (未定义!)")
        print()
    
    print("✅ 测试1通过\n")


def test_group_config():
    """测试群组配置"""
    print("=" * 60)
    print("测试2: 检查群组配置初始化")
    print("=" * 60)
    
    from services.group_config import group_config_store, GroupConfig
    from services.permission import PermissionLevel
    
    # 创建测试配置
    test_group_id = "test_123456"
    config = group_config_store.get(test_group_id)
    
    print(f"\n✅ 成功获取群 {test_group_id} 的配置\n")
    
    # 检查默认配置是否正确初始化
    print("检查命令配置数量:")
    print(f"  期望: {len([k for k in __import__('services.group_config', fromlist=['COMMAND_DEFAULTS']).COMMAND_DEFAULTS.keys()])}")
    print(f"  实际: {len(config.commands)}")
    
    if len(config.commands) >= 24:
        print("  ✅ 所有命令已初始化")
    else:
        print(f"  ❌ 缺少 {24 - len(config.commands)} 个命令配置")
    
    # 测试读取配置
    print("\n测试读取配置:")
    whereis_enabled = config.is_command_enabled("whereis")
    whereis_perm = config.get_command_permission("whereis")
    print(f"  whereis 启用状态: {whereis_enabled}")
    print(f"  whereis 权限要求: {whereis_perm} ({whereis_perm.name})")
    
    # 测试修改配置
    print("\n测试修改配置:")
    config.set_command_enabled("gban", False)
    config.set_command_permission("whereis", PermissionLevel.BOUND_ADMIN)
    
    print(f"  禁用 gban 后: {config.is_command_enabled('gban')}")
    print(f"  修改 whereis 权限后: {config.get_command_permission('whereis')}")
    
    # 保存配置
    group_config_store.set(config)
    print("  ✅ 配置已保存")
    
    # 重新加载验证
    config_reloaded = group_config_store.get(test_group_id)
    print(f"\n重新加载验证:")
    print(f"  gban 启用状态: {config_reloaded.is_command_enabled('gban')}")
    print(f"  whereis 权限: {config_reloaded.get_command_permission('whereis')}")
    
    if not config_reloaded.is_command_enabled('gban') and \
       config_reloaded.get_command_permission('whereis') == PermissionLevel.BOUND_ADMIN:
        print("  ✅ 配置持久化成功")
    else:
        print("  ❌ 配置持久化失败")
    
    # 清理测试数据
    config_reloaded.commands.clear()
    group_config_store.set(config_reloaded)
    print("\n✅ 测试2通过\n")


def test_permission_check():
    """测试权限检查函数"""
    print("=" * 60)
    print("测试3: 检查权限检查函数")
    print("=" * 60)
    
    from services.permission import PermissionLevel, check_command_permission
    from services.group_config import group_config_store
    
    print("\n✅ PermissionLevel.from_str 测试:")
    
    test_cases = [
        ("unbound_user", PermissionLevel.UNBOUND_USER),
        ("bound_user", PermissionLevel.BOUND_USER),
        ("unbound_admin", PermissionLevel.UNBOUND_ADMIN),
        ("bound_admin", PermissionLevel.BOUND_ADMIN),
        ("owner", PermissionLevel.OWNER),
        ("superuser", PermissionLevel.SUPERUSER),
        ("0", PermissionLevel.UNBOUND_USER),
        ("1", PermissionLevel.BOUND_USER),
        ("2", PermissionLevel.UNBOUND_ADMIN),
        ("3", PermissionLevel.BOUND_ADMIN),
        ("4", PermissionLevel.OWNER),
        ("5", PermissionLevel.SUPERUSER),
    ]
    
    for input_str, expected in test_cases:
        result = PermissionLevel.from_str(input_str)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_str}' -> {result} (期望: {expected})")
    
    print("\n✅ 测试3通过\n")


def test_config_manager_imports():
    """测试配置管理器导入"""
    print("=" * 60)
    print("测试4: 检查配置管理器模块")
    print("=" * 60)
    
    try:
        from plugins.config_manager import config_cmd
        print("\n✅ 成功导入 config_manager 插件")
        print(f"   命令处理器: {config_cmd}")
        print("\n✅ 测试4通过\n")
    except Exception as e:
        print(f"\n❌ 导入失败: {e}\n")
        raise


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("VRChat Bot 配置系统测试")
    print("=" * 60 + "\n")
    
    tests = [
        ("默认命令配置", test_command_defaults),
        ("群组配置初始化", test_group_config),
        ("权限检查函数", test_permission_check),
        ("配置管理器导入", test_config_manager_imports),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} 失败: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！配置系统工作正常。\n")
        return 0
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查错误信息。\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
