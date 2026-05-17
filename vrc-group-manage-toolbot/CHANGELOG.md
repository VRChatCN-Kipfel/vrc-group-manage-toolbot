# Changelog

## v0.3.2 — 2026-05-17

### 🚀 新增功能

#### HTML 渲染服务
- **新增 `services/html_render.py`** — HTML 渲染服务
  - `render_card()` - 卡片渲染（支持主题配置）
  - `render_text()` - 文本渲染（支持主题配置）
  - `render_markdown()` - Markdown 渲染（支持主题配置）
  - 集成 `nonebot-plugin-htmlkit` 实现 HTML 转图片功能
  - 支持外部图片嵌入及尺寸控制

- **新增主题配置系统**
  - 卡片主题配置 (`config/pic/card.theme.json`)
  - 文本主题配置 (`config/pic/text.theme.json`)
  - Markdown 主题配置 (`config/pic/markdown.theme.json`)
  - 支持智能字体识别与自定义字体加载

- **新增模板资源**
  - HTML 模板文件 (`assets/templates/card.html.j2`, `text.html.j2`)
  - CSS 样式文件 (`assets/css/card.css.j2`, `text.css.j2`, `markdown.css.j2`)

- **文档**
  - 新增 `docs/HTML_RENDER.md` - HTML 渲染服务完整指南

#### 定时任务调度器
- **新增 `services/scheduler_service.py`** — 定时任务调度服务
  - 支持间隔任务（Interval）
  - 支持 Cron 表达式任务
  - 支持一次性任务（Date）
  - 提供完整的任务管理功能（查看、暂停、恢复、删除、修改）
  - 任务 ID 唯一性保护与强制覆盖机制

- **文档**
  - 新增 `docs/SCHEDULER_USAGE.md` - 定时任务调度器使用指南

### 🔧 改进

- **权限系统优化** (`services/permission.py`)
  - 修复 MessageEvent 类型不安全导致崩溃问题
  - 优化权限检查逻辑

- **CSS 注入逻辑优化** (`services/html_render.py`)
  - 统一在 `<head>` 中添加 style 块
  - 优化模板渲染函数命名以提高可读性

- **依赖更新** (`pyproject.toml`)
  - 新增 `nonebot-plugin-htmlkit` 依赖
  - 新增 `nonebot-plugin-apscheduler` 依赖

### 📁 文件变更

```
+(新增) services/html_render.py          # HTML 渲染服务
+(新增) services/scheduler_service.py    # 定时任务调度器
+(新增) assets/templates/*.html.j2       # HTML 模板文件
+(新增) assets/css/*.css.j2              # CSS 样式文件
+(新增) config/pic/*.theme.json          # 主题配置文件
+(新增) docs/HTML_RENDER.md              # HTML 渲染文档
+(新增) docs/SCHEDULER_USAGE.md          # 定时任务文档
M services/permission.py                 # 修复类型安全问题
M pyproject.toml                         # 新增依赖
M docs/README.md                         # 更新文档索引
```

---

## v0.3.1 — 2026-05-10

### 🐛 修复

- **MessageEvent 类型安全** (`services/permission.py`)
  - 修复 MessageEvent 类型不安全导致崩溃问题
  - 确保权限检查函数能正确处理不同类型的事件

### 🔧 改进

- **代码清理**
  - 移除未使用的导入和变量
  - 优化错误处理逻辑

---

## v0.3.0 — 2026-05-08

### 🚀 重大安全升级：群组绑定模型全面转换

#### 核心变更

**群聊中完全禁止携带 `grp_xxx` 参数** - 所有群组管理指令强制使用已绑定的 VRChat 群组，防止越权操作。

这一变更解决了关键安全问题：
- ❌ **修复前**：甲群管理员可通过 `#gkick(或任意管理指令) grp_{乙群gid} usr_xxx` 管理乙群
- ✅ **修复后**：所有指令自动使用当前 QQ 群绑定的 VRChat 群组，参数被忽略

#### 新增功能

- **新增 `plugins/group_bind.py`** — QQ 群与 VRChat 群组绑定管理系统
  - `#bindgroup` 查询当前群绑定状态（任何人可用）
  - `#bindgroup <grp_xxx>` 绑定当前群到指定 VRChat 群组（仅超管）
  - `#bindgroup unbind` 解除当前群绑定（仅超管）
  - `#bindgroup <grp_xxx> <QQ号>` 私聊中为指定群绑定（仅超管）
  - 支持一个 VRChat 群组绑定到多个 QQ 群
  - 一个 QQ 群只能绑定到一个 VRChat 群组（唯一性约束）

- **新增 `services/group_config.get_by_vrc_group()`** — 反向查询方法
  - 根据 VRChat 群组 ID 查找所有绑定的 QQ 群
  - 用于 `#bindgroup` 查询时显示关联的 QQ 群列表

#### 指令行为变更

**群组管理指令（12个）** - 移除 `grp_xxx` 参数支持：

| 指令 | 原用法 | 新用法（群聊） |
|------|--------|--------------|
| `#gmembers` | `#gmembers grp_xxx [页]` | `#gmembers [页]` |
| `#ginvite` | `#ginvite grp_xxx usr_xxx` | `#ginvite usr_xxx` |
| `#gkick` | `#gkick grp_xxx usr_xxx` | `#gkick usr_xxx` |
| `#gban` | `#gban grp_xxx usr_xxx` | `#gban usr_xxx` |
| `#gunban` | `#gunban grp_xxx usr_xxx` | `#gunban usr_xxx` |
| `#grole` | `#grole grp_xxx usr_xxx 角色` | `#grole usr_xxx 角色` |
| `#grequests` | `#grequests grp_xxx` | `#grequests` |
| `#gaccept` | `#gaccept grp_xxx usr_xxx` | `#gaccept usr_xxx` |
| `#greject` | `#greject grp_xxx usr_xxx` | `#greject usr_xxx` |
| `#gannounce` | `#gannounce grp_xxx\n标题\n内容` | `#gannounce\n标题\n内容` |
| `#gdelannounce` | `#gdelannounce grp_xxx ann_xxx` | `#gdelannounce ann_xxx` |
| `#gaudit` | `#gaudit grp_xxx` | `#gaudit` |

**查询指令**：
- `#instances` - 群聊中自动显示当前群绑定的 VRChat 群组实例，私聊中超管可指定 `grp_xxx`

#### 技术实现

- **重构 `resolve_group_id()` 函数**
  - 群聊中：强制返回已绑定的 `default_vrc_group`，忽略任何传入参数
  - 私聊中：理论上不应到达（所有指令限制为 `GroupMessageEvent`）

- **简化参数解析逻辑**
  - 移除复杂的 `user_arg_idx` 索引计算
  - 所有指令统一从 `parts[0]` 开始读取用户参数
  - 代码量减少约 30%，可读性提升

- **增强错误提示**
  - 未绑定群组时：明确提示联系超管使用 `#bindgroup` 绑定
  - 所有指令用法提示已更新，移除 `grp_xxx` 参数说明

#### 私聊权限控制

- **所有指令添加私聊超管检查**
  - `#instances`, `#whereis` - 私聊中仅超管可用
  - `#vrclLogin`, `#2fa`, `#vrcCheck` - 私聊中仅超管可用
  - 普通用户私聊会被拒绝，防止滥用 API

#### 迁移指南

**超级管理员首次使用前必须执行**：
```bash
# 在目标 QQ 群中
#bindgroup grp_xxxxxxxx
```

**之后所有管理操作都基于绑定的群组**：
```bash
#gmembers              # 查看绑定的群组成员
#gkick usr_xyz         # 从绑定的群组踢人
#gannounce             # 在绑定的群组发布公告
标题
内容
```

---

## v0.2.3 — 2026-05-08

### 🚀 新增功能

#### 临时权限管理系统
- **新增内存级权限覆盖功能** (`services/permission.py`)
  - `set_temp_permission(qq_id, level)`：为指定用户设置临时权限等级
  - `clear_temp_permission(qq_id)`：清除指定用户的临时权限
  - `get_all_temp_permissions()`：获取当前所有临时权限设置
  - **优先级最高**：临时权限在身份识别时优先于 QQ 身份和绑定状态生效

- **新增配置管理子命令** (`plugins/config_manager.py`)
  - `#bot settemppermission @QQ <权限>`：临时设定某人权限（重启失效）
    - 安全限制：禁止通过此命令赋予 Lv5 (SUPERUSER) 权限
  - `#bot cleartemppermission @QQ`：清除某人临时权限
  - `#bot temppermissions`：查看当前所有临时权限设置列表

### 💡 使用场景
1. **紧急降级**：管理员账号异常时，立即运行 `#bot settemppermission @捣乱的管理 0` 剥夺其权限
2. **临时授权**：给热心成员临时开放管理权限 `#bot settemppermission @热心成员 3`
3. **权限审计**：通过 `#bot temppermissions` 随时检查当前的特权名单

---

## v0.2.2 — 2026-05-08

### 🚀 新增功能

#### 动态配置系统
- **新增 `plugins/config_manager.py`** — 配置管理插件（仅超级管理员）
  - `#bot` 显示帮助信息
  - `#bot status` 查看当前群配置状态
  - `#bot list` 列出所有可配置命令
  - `#bot enable/disable <命令>` 启用/禁用命令
  - `#bot permission <命令> <权限>` 设置权限等级
  - `#bot reset [命令]` 重置配置

#### 六级细粒度权限体系
- **重构 `services/permission.py`**
  - 权限等级从 3 级扩展为 6 级：
    - Lv0: 未绑定普通成员 (UNBOUND_USER)
    - Lv1: 已绑定普通成员 (BOUND_USER)
    - Lv2: 未绑定管理员 (UNBOUND_ADMIN)
    - Lv3: 已绑定管理员 (BOUND_ADMIN)
    - Lv4: 群主 (OWNER)
    - Lv5: 机器人超级管理员 (SUPERUSER)
  - `get_permission_level()` 逻辑升级：同时识别 QQ 身份与 VRChat 绑定状态
  - 临时权限支持：提供内存级权限覆盖接口（`set_temp_permission`）

- **优化默认配置 (`COMMAND_DEFAULTS`)**
  - 查询类命令默认要求 **Lv1 (已绑定成员)**，鼓励用户完成绑定
  - 敏感管理类命令（如封禁、踢人）默认提升至 **Lv4 (群主)**
  - 常规管理类命令默认要求 **Lv3 (已绑定管理员)**

#### 细粒度权限控制
- **扩展 `services/group_config.py`**
  - 新增 `CommandConfig` 模型：单个命令的配置（enabled + permission）
  - 新增 `COMMAND_DEFAULTS`：24个命令的默认配置
  - `GroupConfig` 新增 `commands` 字段：存储每个命令的独立配置
  - 新增方法：`is_command_enabled()`, `get_command_permission()`, `set_command_enabled()`, `set_command_permission()`

- **扩展 `services/permission.py`**
  - 新增 `check_command_permission()`：统一的权限检查函数
    - 检查功能是否启用
    - 检查用户权限等级
    - 返回 (是否允许, 错误消息)

#### 全插件权限集成
- **更新所有插件**：添加统一的权限检查
  - `plugins/group_admin.py`：12个管理命令全部接入权限系统
  - `plugins/user_bind.py`：5个绑定命令接入权限系统
  - `plugins/group_manager.py`：查询命令接入权限系统
  - 替换原有的硬编码权限检查为 `check_command_permission()`

### 🔧 改进

- **按群独立配置**：每个QQ群有独立的命令开关和权限设置
- **默认配置自动填充**：新群或新命令自动获得合理的默认值
- **配置持久化**：所有修改立即保存到 `data/vrc_toolbot/group_configs.json`
- **友好的错误提示**：权限不足时明确告知需要的权限等级
- **文档完善**：新增 `CONFIG_GUIDE.md` 详细使用说明

### 📁 文件变更

```
+(新增) plugins/config_manager.py       # 配置管理插件
+(新增) CONFIG_GUIDE.md                 # 配置系统使用指南
M services/group_config.py              # 扩展命令配置功能
M services/permission.py                # 新增权限检查函数
M services/__init__.py                  # 导出新组件
M plugins/group_admin.py                # 集成权限检查
M plugins/user_bind.py                  # 集成权限检查
M plugins/group_manager.py              # 集成权限检查
M README.md                             # 更新文档
```

### 💡 使用场景

1. **临时禁用功能**：`#bot disable instances`（API故障时）
2. **提高敏感操作权限**：`#bot permission gban superuser`
3. **开放查询功能**：`#bot permission whereis user`
4. **批量关闭管理**：逐个 `#bot disable gxxx` 命令
5. **快速恢复默认**：`#bot reset`

---

## v0.2.1 — 2026-05-08

### 🐛 修复

- **`vrc_client.py` 重复方法** — `leave_instance`/`refresh_auth` 各有两个定义导致覆盖，第一个 `refresh_auth` 错误信息写为"加入实例异常"
- **2FA 并发安全** — `_pending_2fa: bool` 改为 `set[str]` 按用户隔离，30 秒超时自动清理
- **`#vrcCheck` FinishedException** — `finish()` 在 `try/except Exception` 内被误捕获，导致"登录成功"后再输出"检查失败: FinishedException()"
- **`#unbind`/`#gannounce` 确认提示** — `.got()` 的 `prompt` 参数不支持 `{key}` 插值，改用 handler 中手动 `send()`
- **Basic Auth 编码** — `verify_2fa()` 中手动 base64 改为 `httpx.BasicAuth`，避免密码含 `:` 时出错
- **`#gmembers` 消息分段** — `send_long_message()` 末尾 chunk 改为 `finish()` 确保 matcher 正确关闭
- **Pydantic v2 弃用 API** — `@validator`/`@root_validator` → `@field_validator`/`@model_validator`
- **默认群配置持久化** — `GroupConfigStore.get()` 新建默认配置后自动 `_save()` 写入磁盘
- **`utils/__init__.py` 导入路径** — 模型类从 `vrc_models` 导入（之前从 `VRC/__init__` 导入会失败但未被触发）
- **版本号** — `pyproject.toml` 从 `0.1.0` 同步到 `0.2.0`

### 🔧 改进

- **死代码清理** — 移除 `VRC/__init__.py` 中未使用的 `asyncio`/`_lock`/`get_vrc_client_safe`
- **冗余代码** — 移除 `vrc_config.py` 中 5 处 `or None` 冗余
- **变量统一** — `#instances` 中多余的 `get_vrc_client()` 调用统一为 `client` 变量
- **类型安全** — `api_guard.cache_set()` 中 `ttl` 添加 `float()` 转换
- **Shutdown 钩子** — `bot.py`/`run.py` 注册 `driver.on_shutdown` 优雅关闭 HTTP 客户端

---

## v0.2.0 — 2026-05-07

### 🚀 新增功能

#### 插件系统
- **新增 `plugins/group_admin.py`** — 12 个 VRChat 群管理命令
  - `#gmembers` 分页群成员列表
  - `#ginvite` / `#gkick` / `#gban` / `#gunban` 成员管理
  - `#grole` 角色设置（模糊匹配）
  - `#grequests` / `#gaccept` / `#greject` 入群审核
  - `#gannounce` / `#gdelannounce` 公告管理
  - `#gaudit` 审核日志
- **新增 `plugins/user_bind.py`** — QQ ↔ VRChat 用户绑定系统
  - `#bind` BIO 验证码绑定（3 分钟过期）
  - `#bind force` 管理员强制绑定
  - `#confirm` / `#unbind` 确认与解绑
  - `#bindinfo` / `#whois` 绑定信息与状态查询
- **新增 `#2fa` 命令** — 交互式两步验证流程
- **新增 `#vrclLogin cookie=xxx`** — 浏览器 Cookie 直登，跳过用户名密码 + 2FA

#### 服务层
- **新增 `services/`** — 插件与后端之间的胶水层
  - `api_guard.py` — 速率控制（≥1.5s）+ 指数退避重试 + TTL 缓存
  - `permission.py` — 三级权限（USER/GROUP_ADMIN/SUPERUSER）+ VRChat 角色检查
  - `message_utils.py` — 消息格式化/分段（>3800 字符自动拆分）
  - `user_binding.py` — 绑定数据 CRUD（JSON 持久化）
  - `group_config.py` — 每 QQ 群独立配置

#### VRChat API 客户端
- 新增 14 个群管理 API 端点（成员/角色/公告/审核/封禁）
- 新增 `_request()` 统一请求层，HTTP 错误上抛给 api_guard
- 新增 `verify_2fa()` 独立两步验证方法
- User 模型增加 `bio`/`bioLinks` 字段
- Instance 模型增加 `instanceId` 别名

### 🔧 改进

- **命令触发**：移除所有 `rule=to_me()`，直接 `#` 前缀触发
- **命令前缀**：`/` 改为 `#`（避免 QQ 内 `/` 被转为表情）
- **API 调用**：旧方法（`get_user`/`get_instance`/`get_group` 等）改用 `_request()`，401/429 等错误正确传播到 api_guard 处理
- **登录**：POST + form-data 改为 GET + Basic Auth
- **启动**：修复 `nonebot.run(app="bot:app")` 导致的双重初始化
- **2FA**：分离 `verify_2fa()` 方法，不再每次重新 GET `/auth/user`

### 🐛 修复

- `Instance` 模型重复 `class Config` 导致 `populate_by_name` 被覆盖
- `FinishedException` 被 `try/except Exception` 捕获导致错误信息异常
- `#whereis` / `#instances` 参数类型错误（`MessageEvent` → `Message`）导致 handler 被跳过
- 三个插件各自独立 `get_vrc_client()` 单例 → 统一为 `utils/VRC` 内的共享实例
- `api_guard` 将 `None` 返回值当成功 → 配合 `_request()` 异常传播修复

### 📁 目录重构

```
utils/vrc_client.py  →  utils/VRC/vrc_client.py
utils/vrc_config.py  →  utils/VRC/vrc_config.py
utils/vrc_models.py  →  utils/VRC/vrc_models.py
utils/__init__.py    →  重新从 VRC 子包导出
+(新增) services/    →  5 个新文件
+(新增) plugins/group_admin.py, user_bind.py
```

### 🔧 后续修复（同日）

- **`#instances` 显示完善** — 提取 `world.name` 作为世界名、`world.capacity` 作为容量、解析 `location` 获取在线人数
- **`#vrcCheck` 命令** — 快速验证登录状态，不触发重认证
- **Cookie 持久化** — 登录成功自动保存到 `data/auth_cookie.txt`，重启免登录
- **`Instance` 模型修复** — `world` 字典自动展开为 `worldId`/`worldName`/`capacity`
- **`Instance` 模型** — `memberCount` 映射为 `userCount`，`instanceId` 别名
- **`n_users` 验证器** — 兼容 API 返回 `0`（整数）而非空数组
- **登录流程** — 已有 cookie 时不再因为响应无新 cookie 而误判失败
- **重复消息修复** — 删除 `#instances`/`#whereis` 中重复的 `send()` 调用
- **实例 ID 修复** — 传入完整 `location`（含 `~group()` 标签）获取准确在线人数

---

## v0.1.0 — 2026-05-06

### 初始版本

- NoneBot2 + OneBot V11 框架搭建
- VRChat API 基础客户端（登录、用户查询、实例查询）
- `#instances` / `#whereis` / `#vrclLogin` 三个基础命令
