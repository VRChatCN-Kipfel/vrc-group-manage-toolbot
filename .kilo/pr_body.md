## v0.2.1 代码审查修复

基于对 `vrc-group-manage-toolbot` 项目的全面代码审查（16 个源文件，~1200 行），修复如下：

### Bug 修复
- **`vrc_client.py` 重复方法** — `leave_instance`/`refresh_auth` 各有两个定义导致覆盖
- **2FA 并发安全** — `_pending_2fa: bool` → `set[str]` 按用户隔离，30秒超时自动清理
- **`#vrcCheck` FinishedException** — `finish()` 在 `try/except` 内被误捕获导致二次报错
- **`#unbind`/`#gannounce` 确认提示** — `.got()` 的 `prompt` 不支持 `{key}` 插值，改用手动 `send()`
- **Basic Auth 编码** — `verify_2fa()` 手动 base64 → `httpx.BasicAuth`，避免密码含 `:` 时报错
- **`send_long_message()`** — 末尾 chunk 改用 `finish()` 确保 matcher 正确关闭
- **`GroupConfigStore.get()`** — 新建默认配置后自动持久化到磁盘
- **`utils/__init__.py`** — 模型类改为从 `vrc_models` 正确导入

### 改进
- Pydantic v2 API 迁移（`@validator` → `@field_validator`）
- 移除 `VRC/__init__.py` 死代码（`_lock`/`get_vrc_client_safe`）
- `vrc_config.py` 移除 5 处冗余 `or None`
- `api_guard.cache_set()` 添加 `float()` 类型转换
- `bot.py`/`run.py` 注册 shutdown 钩子优雅关闭 HTTP 客户端
- `pyproject.toml` 版本号同步到 `0.2.0`
- CHANGELOG + TESTING 同步更新

### 文件统计
14 个文件，+60 / -102 行
