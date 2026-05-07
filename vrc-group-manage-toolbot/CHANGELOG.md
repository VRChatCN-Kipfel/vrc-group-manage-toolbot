# Changelog

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
