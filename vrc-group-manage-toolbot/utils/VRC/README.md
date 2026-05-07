# VRChat API 客户端 - 架构说明

## 项目结构

```
vrc-group-manage-toolbot/
├── utils/                          # 工具模块目录
│   ├── __init__.py                # 导出 VRC 子模块
│   └── VRC/                        # VRChat API 客户端子包
│       ├── __init__.py            # 导出客户端类和模型
│       ├── vrc_client.py          # VRCClient - VRChat API 客户端（工具类）
│       ├── vrc_config.py          # VRCConfig - 配置管理
│       ├── vrc_models.py          # 数据模型定义
│       └── README.md              # 本说明文档
│
├── plugins/                        # 功能插件目录
│   ├── group_manager.py           # 群组管理插件（使用 VRC）
│   └── ...                         # 其他插件
│
└── .env                           # 环境变量配置
```

## 架构设计原则

### 1. **VRC 是工具模块包**
- 位置: `utils/VRC/`
- 职责: 提供与 VRChat API 交互的底层功能
- 特点: 
  - 封装在独立的子包中
  - 可被多个插件复用
  - 不直接处理用户消息
  - 通过 `from utils import VRC` 整体导入

### 2. **Plugins 是功能插件**
- 位置: `plugins/*.py`
- 职责: 实现具体的业务逻辑和用户交互
- 特点:
  - 监听用户命令
  - 调用 VRC 执行 API 操作
  - 处理并返回结果给用户

## 使用示例

### 在插件中使用 VRC

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from ..utils import VRC

# 创建命令处理器
my_command = on_command("mycmd")

# 获取客户端实例（推荐单例模式）
def get_client() -> VRC.VRCClient:
    config = VRC.VRCConfig.from_env()
    return VRC.VRCClient(config)

@my_command.handle()
async def handle_command(event: MessageEvent, args: MessageEvent = CommandArg()):
    # 1. 解析用户输入
    group_id = args.extract_plain_text().strip()
    
    # 2. 获取客户端
    client = get_client()
    
    # 3. 调用 API
    group = await client.get_group(group_id)
    
    # 4. 处理结果并回复
    if group:
        await my_command.finish(f"群组: {group.name}")
    else:
        await my_command.finish("未找到群组")
```

## 核心组件

### VRC 子包结构

**核心组件:**

#### VRC Client (VRC/vrc_client.py)

提供以下 API 方法：

**认证相关:**
- `login()` - 登录
- `refresh_auth()` - 刷新认证
- `is_authenticated` - 检查认证状态

**用户相关:**
- `get_current_user()` - 获取当前用户
- `get_user(user_id)` - 获取指定用户

**实例相关:**
- `get_instance(instance_id)` - 获取实例信息
- `join_instance(instance_id)` - 加入实例
- `leave_instance(instance_id)` - 离开实例

**群组相关:**
- `get_group(group_id)` - 获取群组信息
- `get_group_instances(group_id)` - 获取群组实例列表

**世界相关:**
- `get_world(world_id)` - 获取世界信息

#### 数据模型 (VRC/vrc_models.py)

- `User` - 用户模型
- `Instance` - 实例模型
- `Group` - 群组模型
- `World` - 世界模型

#### 配置管理 (VRC/vrc_config.py)

从 `.env` 文件加载配置：
```env
VRC_USERNAME="your_username"
VRC_PASSWORD="your_password"
VRC_AUTH_COOKIE=""
VRC_TIMEOUT=30
VRC_REQUEST_DELAY=1000
```

## 最佳实践

1. **整体导入**: 使用 `from utils import VRC` 导入整个模块
2. **命名空间访问**: 通过 `VRC.VRCClient`、`VRC.VRCConfig` 等方式访问
3. **单例模式**: 在插件中使用全局变量保存客户端实例，避免重复创建
4. **错误处理**: 所有 API 调用都应该有 try-except 保护
5. **日志记录**: 使用 `logger` 记录关键操作和错误
6. **用户提示**: 在执行耗时操作时，先发送"正在处理..."提示

## 扩展示例

创建新的插件时，只需：

1. 在 `plugins/` 目录创建新文件
2. 导入 `VRC` 模块
3. 实现命令处理逻辑
4. 调用 VRC 中的类和方法

例如创建 `world_info.py`:

```python
from nonebot import on_command
from ..utils import VRC

world_cmd = on_command("world")

@world_cmd.handle()
async def handle_world(args):
    world_id = args.extract_plain_text()
    client = VRC.VRCClient(VRC.VRCConfig.from_env())
    world = await client.get_world(world_id)
    # ... 处理结果
```

## 导入方式对比

### ✅ 推荐方式（整体导入）


```python
from utils import VRC

client = VRC.VRCClient(...)
config = VRC.VRCConfig.from_env()
user = VRC.User(...)
```

### 备选方式（直接导入子模块）


```python
from utils.VRC import VRCClient, VRCConfig, User

client = VRCClient(...)
config = VRCConfig.from_env()
user = User(...)
```
