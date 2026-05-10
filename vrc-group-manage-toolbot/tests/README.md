# 测试套件说明

## 目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和 fixtures
├── README.md                # 本文件
├── services/                # Services 层测试
│   └── __init__.py          # 服务层测试用例
├── plugins/                 # Plugins 层测试
│   └── __init__.py          # 插件层测试用例
└── utils/                   # Utils 层测试
    └── __init__.py          # 工具层测试用例
```

## 测试策略

### 虚测（Virtual Tests）
- **目的**：验证模块导入、配置合法性、数据结构等
- **特点**：不需要 Bot 环境，快速执行
- **示例**：
  - 模块是否可以正常导入
  - 命令定义是否完整
  - 配置字段是否正确
  - 权限级别转换逻辑

### 实测试（Real Tests）
- **目的**：模拟真实 Bot 环境，测试功能交互
- **特点**：使用 nonebug 创建 mock Bot，测试完整流程
- **示例**：
  - 配置持久化
  - 命令响应
  - 权限验证
  - 消息处理

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/services/ -v
pytest tests/plugins/ -v
pytest tests/utils/ -v

# 运行特定测试类
pytest tests/services/__init__.py::TestGroupConfig -v

# 运行特定测试方法
pytest tests/services/__init__.py::TestGroupConfig::test_command_defaults_exist -v

# 显示详细输出
pytest tests/ -v -s

# 生成覆盖率报告
pytest tests/ --cov=services --cov=plugins --cov=utils --cov-report=html
```

## 编写新测试

### 虚测示例

```python
@pytest.mark.asyncio
async def test_module_import():
    """虚测：验证模块可导入"""
    from services.xxx import some_function
    assert some_function is not None
```

### 实测试示例

```python
@pytest.mark.asyncio
async def test_feature_with_bot(app: App, test_group_id: str):
    """实测试：使用 mock Bot 测试功能"""
    from tests import create_mock_bot
    
    # 创建模拟 Bot
    bot, ctx = await create_mock_bot(app)
    
    # 使用 fixture 提供的测试 ID
    config = group_config_store.get(test_group_id)
    
    # 测试逻辑
    # ...
    
    # 验证结果
    assert result == expected
```

### 可用的工具函数

```python
from tests import create_mock_bot, get_test_group_id, get_test_user_id

# 创建 mock bot
bot, ctx = await create_mock_bot(app)
bot, ctx = await create_mock_bot(app, self_id="123456789")  # 自定义 Bot ID

# 生成测试 ID
group_id = get_test_group_id(1)  # "100000001"
user_id = get_test_user_id(1)    # "1000000001"
```

### 可用的 Fixtures

```python
# 测试数据生成 fixtures
@pytest.mark.asyncio
async def test_something(test_group_id: str, test_user_id: str):
    # test_group_id: "100000001"
    # test_user_id: "1000000001"
    pass

# 自动清理 fixtures（推荐用于需要清理的测试）
@pytest.mark.asyncio
async def test_with_cleanup(cleanup_after_test):
    # 测试逻辑...
    # 测试结束后自动清理群组配置
    pass

@pytest.mark.asyncio
async def test_user_cleanup(cleanup_user_after_test):
    # 测试逻辑...
    # 测试结束后自动清理用户绑定
    pass
```

## 注意事项

1. **路径配置**：`tests/__init__.py` 在模块导入时自动配置项目根目录到 Python 路径
2. **群 ID 格式**：使用 `get_test_group_id()` 生成纯数字字符串，符合 OneBot 规范
3. **Mock Bot 创建**：使用 `create_mock_bot()` 工具函数，不要直接在测试中创建
4. **数据清理**：使用 `cleanup_after_test` fixture 自动清理，无需手动处理
5. **异步测试**：所有测试函数都应使用 `@pytest.mark.asyncio` 装饰器
6. **职责分离**：
   - `tests/__init__.py` - 路径配置 + 纯工具函数（无副作用，可被任何代码调用）
   - `tests/conftest.py` - pytest 专属 fixtures（生命周期管理，包含 setup/teardown 逻辑）
   - 各模块测试文件 - 具体的测试用例
