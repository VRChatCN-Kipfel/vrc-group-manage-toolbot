# 整合报告：六级权限 + 临时权限 + 群组绑定安全模型

> **分支**: local/pr-integrated -> master  
> **基准**: upstream/master  
> **日期**: 2026-05-09  
> **整合人**: AfterGlow.SYX

---

## 概述

将上游 3 个独立 PR 分支合入 master，经过合并冲突解决、4 轮代码审查、20+ 项 bug 修复和有限功能实测。

### 上游 PR 来源

| 分支 | 原始 PR | 功能 | 原始作者 |
|------|---------|------|----------|
| feat-permission-Patch-1 | #2 | 六级细粒度权限体系 + #bot 动态配置管理 | XChen446 |
| feat-permission-Patch-2 | #3 | 内存级临时权限设置/清除/查询 | XChen446 |
| feat-group-Patch-1 | #4 | 群组绑定安全模型重构（移除 grp_xxx 参数） | XChen446 |

### 合并挑战

三个分支同时修改了 group_admin.py、group_manager.py、permission.py、CHANGELOG.md、README.md，单独合并会产生大量冲突。整合到一个分支后分阶段合并：

Phase 1: feat-permission-Patch-1 -> 修复 3 个已知 bug
Phase 2: feat-permission-Patch-2 -> 修复 2 个遗漏项
Phase 3: feat-group-Patch-1 -> 修复 3 个 bug
Phase 4: 手动解决 5 个文件的合并冲突
Phase 5+: 4 轮审查修复（20+ 项）

---

## 变更清单

16 个文件，**+2,177 / -287 行**。

### 全新文件（4 个）

| 文件 | 说明 |
|------|------|
| plugins/config_manager.py | #bot 配置管理插件（364 行） |
| plugins/group_bind.py | #bindgroup 群组绑定插件（204 行） |
| CONFIG_GUIDE.md | 配置系统详细使用指南 |
| test_config.py | 六级权限系统单元测试 |

### 重构文件

| 文件 | 变更幅度 | 核心改动 |
|------|----------|----------|
| plugins/group_admin.py | +349/-288 | 移除 grp_xxx 参数，resolve_group_id 简化，skip_grp_prefix 添加，权限检查集成 |
| services/permission.py | +135/-30 | 六级枚举，from_str 修复，check_command_permission，_temp_permissions 模块 |
| services/group_config.py | +96/-20 | CommandConfig 模型，COMMAND_DEFAULTS（24 个命令），get_by_vrc_group() |
| plugins/group_manager.py | +92/-33 | 私聊超管限制，instances 绑定集成，2FA cookie 修复，aliases=list |

### 其他修改

| 文件 | 性质 |
|------|------|
| CHANGELOG.md | 新增 v0.2.2 / v0.2.3 / v0.3.0 |
| README.md | 六级权限表格，cleartemppermission 命令，项目结构更新 |
| .gitignore | .env / data/ / __pycache__/ |
| utils/VRC/vrc_client.py | 2FA cookie 按用户隔离 |
| plugins/user_bind.py | 分隔线字符替换 |
| services/__init__.py | 导出新组件 |

---

## 审查修复（4 轮，共 20+ 项）

### 第一轮（合并后自查）

| 问题 | 影响 | 状态 |
|------|------|------|
| from_str 无效输入静默回退为 UNBOUND_USER | 配置错误无法发现 | 已修 |
| test_config.py 引用旧枚举 GROUP_ADMIN / USER | 测试运行失败 | 已修 |
| 帮助文本显示三级权限格式 | 用户困惑 | 已修 |
| cleartemppermission 命令未接线 | 临时权限无法清除 | 已修 |
| sender.role 在 PrivateMessageEvent 无此属性 | 私聊崩溃 | 已修 |
| grole 参数解析索引错位 | 角色设置失败 | 已修 |
| resolve_group_id 死代码 isinstance 检查 | 代码混乱 | 已修 |

### 第二轮（深度零上下文审查）

| 问题 | 影响 | 状态 |
|------|------|------|
| #bot settemppermission @QQ 永远报错 | 临时权限核心功能不可用 | 已修 |
| _temp_permissions TOCTOU 竞态 | 并发下 KeyError | 已修 |
| 2FA cookie 多用户竞态 | 并发登录互相覆盖 | 已修 |
| _pending_2fa task 泄漏+重登录杀活跃 session | 2FA 永久失效 | 已修 |
| resolve_group_id 死参数 text_parts | 代码质量 | 已修 |
| from_str 输入未 .strip() | 首尾空格失败 | 已修 |

### 第三轮（修复后验证）

| 问题 | 影响 | 状态 |
|------|------|------|
| parts[-1] -> parts[1] | settemppermission 多余参数被误读 | 已修 |
| resolve_group_id 返回类型 str -> Optional[str] | 类型不准 | 已修 |
| 残留 global _pending_2fa | 代码误解 | 已修 |

### 第四轮（第三方深度审查后批量修复）

| 问题 | 影响 | 状态 |
|------|------|------|
| PermissionLevel.USER 幽灵枚举（#bot reset 后崩溃） | bot 完全不可用 | 已修 |
| _pending_2fa_task 重登录覆盖旧 task | 活跃 2FA session 被杀 | 已修 |
| _pending_2fa_cookies.pop 在网络请求前执行 | 网络失败后 cookie 丢失 | 已修 |
| config_manager.py 私聊无守卫 | 私聊 #bot 崩溃 | 已修 |
| Cookie 登录 except 块 client 未绑定 | NameError | 已修 |
| 单行 #gannounce 被拒 | 可用性问题 | 已修 |
| 11 个管理命令缺 require_auth 预检 | 浪费 API 重试 | 已修 |
| instances/whereis 未用 send_long_message | 长消息截断 | 已修 |
| 翻页提示 /gmembers -> #gmembers | 用户复制无效命令 | 已修 |
| check_vrc_group_role 异常静默吞掉 | 无日志诊断 | 已修 |
| NapCatQQ @段丢失 -> event.raw_message 回退 | cleartemppermission 失败 | 已修 |
| NapCatQQ 消息渲染分隔线字符错乱 | 帮助文本重复 30 遍 | 已修 |

---

## 测试状态

| 状态 | 数量 |
|------|------|
| 已测通过 | 25 |
| 未测试 | 44 |
| 已知问题 | 1（Cookie 直登跨域，底层 API 限制） |

### 已测通过摘要

| 模块 | 通过项 |
|------|--------|
| 认证 | 登录、2FA、状态检查、Cookie 持久化 |
| 配置管理 | #bot, status, list, enable, disable, reset |
| 临时权限 | settemppermission, cleartemppermission（@解析已修复） |
| 群组绑定 | 群聊查询/绑定/解绑，私聊查询/绑定/解绑 |
| 查询 | whereis, bind, confirm, bindinfo, whois, unbind, bind force |
| 安全 | .env gitignore，凭据未泄露 |

### 待测（按模块）

| 模块 | 待测数 | 说明 |
|------|--------|------|
| #bot permission 及拒绝 | 7 | 权限设置子命令、非超管/私聊拒绝 |
| 临时权限 | 7 | temppermissions 查看、Lv5 禁止、临权优先级、重启清空 |
| 群组绑定边界 | 5 | 非超管拒绝、重复绑定、未绑定解绑 |
| 私聊限制 | 5 | 非超管私聊 vrclLogin/2fa/vrcCheck/instances/whereis |
| 群管理命令 | 14 | 12 个 gxxx 命令、旧格式兼容、未绑定提示 |
| 查询命令 | 3 | instances 群聊/私聊、参数忽略 |
| 命令开关联动 | 4 | 禁用+超管拦截、启用生效、权限修改、reset 恢复 |
| 边界测试 | 5 | 重启清空临权、无@提示、无效命令、Cookie 直登 |

---

## 安全审查

| 检查项 | 状态 |
|--------|------|
| .env 在 .gitignore 中，未追踪 | OK |
| 凭据未出现在 .py 源码中 | OK |
| QQ 号/群号未硬编码在源码中 | OK |
| VRC_USERNAME / VRC_PASSWORD 仅在 .env（已忽略） | OK |
| settemppermission 禁止赋予 SUPERUSER（Lv5） | OK |
| 私聊管理命令仅超管可用 | OK |
| #bot 配置管理仅超管可用 | OK |
