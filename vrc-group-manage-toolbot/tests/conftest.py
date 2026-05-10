"""
pytest 配置文件

职责：
1. 提供测试数据 fixtures（引用 __init__.py 中的函数）
2. 管理测试生命周期（setup/teardown）
3. pytest 专属配置
"""
import pytest
from tests import get_test_group_id, get_test_user_id


# ============================================================================
# Fixtures - 测试数据生成（引用 __init__.py 中的函数）
# ============================================================================

@pytest.fixture
def test_group_id():
    """
    提供测试用的群 ID
    
    使用方式：
        def test_something(test_group_id):
            # test_group_id = "100000001"
            pass
    """
    return get_test_group_id()


@pytest.fixture
def test_user_id():
    """
    提供测试用的用户 ID
    
    使用方式：
        def test_something(test_user_id):
            # test_user_id = "1000000001"
            pass
    """
    return get_test_user_id()


# ============================================================================
# Fixtures - 测试生命周期管理（setup/teardown）
# ============================================================================

@pytest.fixture
def cleanup_after_test(test_group_id):
    """
    测试后自动清理群组配置数据
    
    职责：
    - yield 前：setup（可选）
    - yield：测试执行点
    - yield 后：teardown（清理）
    
    使用方式：
        def test_something(cleanup_after_test):
            # 测试逻辑...
            # 测试结束后自动清理
            pass
    """
    yield  # 测试执行点
    
    # ===== Teardown: 测试后清理 =====
    from services.group_config import group_config_store
    config = group_config_store.get(test_group_id)
    if config:
        config.commands.clear()
        group_config_store.set(config)


@pytest.fixture
def cleanup_user_after_test(test_user_id):
    """
    测试后自动清理用户绑定数据
    
    职责：
    - yield 前：setup（可选）
    - yield：测试执行点
    - yield 后：teardown（清理）
    
    使用方式：
        def test_something(cleanup_user_after_test):
            # 测试逻辑...
            # 测试结束后自动清理
            pass
    """
    yield  # 测试执行点
    
    # ===== Teardown: 测试后清理 =====
    from services.user_binding import user_binding_store
    if test_user_id in user_binding_store._bindings:
        del user_binding_store._bindings[test_user_id]
        user_binding_store._save()

# ============================================================================
# Hooks - pytest hooks for forced cleanup after test crashes
# ============================================================================

def pytest_sessionfinish(session, exitstatus):
    from services.group_config import group_config_store
    from services.user_binding import user_binding_store
    
    for gid in list(group_config_store._configs.keys()):
        if str(gid).startswith("10000000"):
            config = group_config_store._configs[gid]
            config.commands.clear()
            group_config_store.set(config)
    
    for uid in list(user_binding_store._bindings.keys()):
        if str(uid).startswith("10000000"):
            del user_binding_store._bindings[uid]
    user_binding_store._save()

