# 测试状态

## 已完成测试 ✅

### 认证模块
| 功能 | 命令 | 结果 |
|------|------|------|
| 用户名密码登录 | `#vrclLogin` | ✅ 正常 |
| 两步验证 | `#2fa 验证码` | ✅ 401 bug已修，验证码提交交互正常 |
| 登录状态检查 | `#vrcCheck` | ✅ 正常 |
| Cookie 持久化 | 重启自动加载 | ✅ 重启免登录 |
| 私聊非超管拒登 | 非超管私聊 `#vrclLogin` | ❓ 未实测 |

### 配置系统 (`#bot` — 仅超管)
| 功能 | 命令 | 结果 |
|------|------|------|
| 帮助信息 | `#bot` | ✅ 正常（分隔线渲染问题已修） |
| 群配置状态 | `#bot status` | ✅ 正常 |
| 命令列表 | `#bot list` | ✅ 正常，按模块分组 |
| 启用命令 | `#bot enable <命令>` | ✅ 正常 |
| 禁用命令 | `#bot disable <命令>` | ✅ 正常 |
| 设置权限 | `#bot permission <命令> <等级>` | ❌ 未测 |
| 重置配置 | `#bot reset [命令]` | ✅ 正常，model_post_init 已修复 |
| 非超管拒绝 | 普通用户发 `#bot` | ❌ 未测 |
| 私聊拒绝 | 私聊发 `#bot` | ❌ 未测 |

### 临时权限
| 功能 | 命令 | 结果 |
|------|------|------|
| 设置临时权限 | `#bot settemppermission @QQ 4` | ✅ @机器人设为群主，正常 |
| 清除临时权限 | `#bot cleartemppermission @QQ` | ✅ @解析问题已修（改用 event.raw_message） |
| 查看临时权限 | `#bot temppermissions` | ❌ 未测 |
| 禁止赋 Lv5 | `#bot settemppermission @QQ 5` | ❌ 未测 |
| 临权优先级 | 临权覆盖真实身份 | ❌ 未测 |
| 清除后恢复 | 临权清除后恢复原身份 | ❌ 未测 |

### 群组绑定 (`#bindgroup`)
| 功能 | 命令 | 结果 |
|------|------|------|
| 群聊查询绑定 | `#bindgroup` | ✅ 显示群组名+ID+关联QQ群 |
| 群聊绑定 | `#bindgroup grp_xxx` | ✅ 正常 |
| 群聊解绑 | `#bindgroup unbind` | ✅ 正常 |
| 私聊查询 | `#bindgroup 1065673490` | ✅ 正常（条件反转bug已修） |
| 私聊绑定 | `#bindgroup grp_xxx 1065673490` | ✅ 正常 |
| 私聊解绑 | `#bindgroup unbind 750834329` | ✅ 正常（残留查询代码已清） |
| 非超管绑/解 | 普通用户 `#bindgroup grp_xxx` | ❌ 未测 |
| 已有绑定再绑 | 已绑定的群再 `#bindgroup grp_其他` | ❌ 未测 |
| 未绑定群解绑 | `#bindgroup unbind` (无绑定) | ❌ 未测 |

### 群组管理（需 VRChat Owner/Mod 权限）
| 功能 | 命令 | 结果 |
|------|------|------|
| 群成员 | `#gmembers` | ❌ 未测 |
| 邀请 | `#ginvite usr_xxx` | ❌ 未测 |
| 踢人 | `#gkick usr_xxx` | ❌ 未测 |
| 封禁 | `#gban usr_xxx` | ❌ 未测 |
| 解封 | `#gunban usr_xxx` | ❌ 未测 |
| 设置角色 | `#grole usr_xxx 角色` | ❌ 未测 |
| 入群申请 | `#grequests` | ❌ 未测 |
| 批准申请 | `#gaccept usr_xxx` | ❌ 未测 |
| 拒绝申请 | `#greject usr_xxx` | ❌ 未测 |
| 发布公告 | `#gannounce` | ❌ 未测 |
| 删除公告 | `#gdelannounce ann_xxx` | ❌ 未测 |
| 审核日志 | `#gaudit` | ❌ 未测 |
| 旧格式兼容 | `#gmembers grp_xxx 2` (skip_grp_prefix) | ❌ 未测 |
| 未绑定群提示 | 解绑后 `#gmembers` | ❌ 未测 |

### 查询命令
| 功能 | 命令 | 结果 |
|------|------|------|
| 群实例 | `#instances` (群聊) | ❌ 未测 |
| 群实例 | `#instances grp_xxx` (私聊超管) | ❌ 未测 |
| 私聊非超管拒绝 | 非超管私聊 `#instances` | ❌ 未测 |
| 用户位置 | `#whereis usr_xxx` | ✅ 正常 |
| 用户绑定 | `#bind` + `#confirm` | ✅ Bio验证码流程通 |
| 绑定信息 | `#bindinfo` | ✅ 正常 |
| 用户状态 | `#whois @某人` | ✅ 正常 |
| 解绑 | `#unbind` | ✅ 二次确认正常 |
| 强制绑定 | `#bind force @QQ usr_xxx` | ✅ 超管正常 |

### 安全性
| 功能 | 结果 |
|------|------|
| `.env` 已加入 `.gitignore` | ✅ |
| 凭据未出现在 `.py` 文件中 | ✅ |
| 私聊限制（vrclLogin/2fa/vrcCheck） | ❌ 未测 |
| 非超管 `#bot` 拒绝 | ❌ 未测 |

---

### 配置热重载服务 🔄

| 功能 | 测试 | 结果 |
|------|------|------|
| ConfigReloadService 构造 | 单元 `test_construction_generation_zero` | ✅ |
| generation 初始值 | 单元 `test_construction_has_observers_empty` | ✅ |
| subscribe 注册回调 | 单元 `test_subscribe_adds_observer` | ✅ |
| subscribe 去重 | 单元 `test_subscribe_dedup` | ✅ |
| unsubscribe 移除 | 单元 `test_unsubscribe_removes_observer` | ✅ |
| unsubscribe 不存在容错 | 单元 `test_unsubscribe_nonexistent_no_error` | ✅ |
| trigger_reload 递增 generation | 单元 `test_trigger_reload_increments_generation` | ✅ |
| 多观察者按注册顺序通知 | 单元 `test_multiple_observers_notified_in_order` | ✅ |
| 单个观察者异常不阻断其他 | 单元 `test_one_observer_failure_does_not_block_others` | ✅ |
| asyncio.Lock 串行化并发重载 | 单元 `test_reload_lock_serializes_concurrent_triggers` | ✅ |
| start_watching 创建监控 task | 单元 `test_start_watching_creates_task` | ✅ |
| stop_watching 取消监控 task | 单元 `test_stop_watching_cancels_task` | ✅ |
| _has_changes 检测新文件 | 单元 `test_has_changes_new_file_detected` | ✅ |
| _has_changes 空目录容错 | 单元 `test_has_changes_empty_dir_no_error` | ✅ |
| subscribe(first=True) 插队首 | 单元 `test_subscribe_first_inserts_at_head` | ✅ |

### 全局配置热重载 🔄

| 功能 | 测试 | 结果 |
|------|------|------|
| 加载默认配置 | 单元 `test_load_default_config` | ✅ |
| verify_code_ttl 默认值 | 单元 `test_verify_code_ttl_default` | ✅ |
| cleanup_interval 默认值 | 单元 `test_cleanup_interval_default` | ✅ |
| reload() 原子替换 features | 单元 `test_reload_atomic_swap_features` | ✅ |
| reload() 原子替换 binding_settings | 单元 `test_reload_atomic_swap_binding` | ✅ |
| 缺失 YAML 文件 reload 不崩溃 | 单元 `test_reload_missing_file_no_crash` | ✅ |
| 损坏 YAML reload 不崩溃 | 单元 `test_reload_corrupted_yaml_no_crash` | ✅ |
| _lock 保护 reload 串行化 | 单元 `test_reload_lock_protects_concurrent` | ✅ |
| 属性读取不被锁阻塞 | 单元 `test_property_reads_not_blocked_by_lock` | ✅ |

### 调度器核心 API 🔄

| 功能 | 测试 | 结果 |
|------|------|------|
| force_replace 覆盖已存在任务 | 单元 `test_add_interval_task_with_force_replace` | ✅ |
| 重复注册抛 TaskAlreadyExistsError | 单元 `test_add_interval_task_duplicate_raises` | ✅ |
| 移除不存在任务抛 JobLookupError | 单元 `test_remove_task_raises_job_lookup_error` | ✅ |
| 获取不存在任务返回 None | 单元 `test_get_task_info_returns_none_for_missing` | ✅ |
| 无 ManagedTaskRegistry 残留 | 单元 `test_no_managed_task_registry` | ✅ |

---

## 未测试（完整清单）

### `#bot` 子命令 (12 项 → 6 项待测)

| # | 命令 | 验证点 |
|---|------|--------|
| 1.1 | `#bot enable bot` | 应拒绝：不能禁用配置管理命令 |
| 1.2 | `#bot permission whereis 0` | 修改 whereis 为 Lv0 |
| 1.3 | `#bot permission whereis bound_user` | 用名称修改权限 |
| 1.4 | `#bot permission bot 0` | 应拒绝：配置管理必须超管 |
| 1.5 | `#bot permission whereis invalid` | 应报错：无效权限等级 |
| 1.6 | 普通用户 `#bot` | 应拒绝：仅超管可用 |
| 1.7 | 私聊 `#bot` | 应拒绝：仅群聊可用 |

### 临时权限 (8 项)

| # | 命令 | 验证点 |
|---|------|--------|
| 2.1 | `#bot settemppermission @某人 0` | 降权生效 |
| 2.2 | `#bot settemppermission @某人 owner` | 用名称设权 |
| 2.3 | `#bot settemppermission @某人 5` | 应拒绝：禁止赋超管 |
| 2.4 | `#bot temppermissions` | 空列表/有数据两种情况 |
| 2.5 | `#bot cleartemppermission @某人` | 清除后 temppermissions 不显示 |
| 2.6 | 临权覆盖真实身份 | 设临时 Lv3 → 普通用户能执行 Lv3 命令 |
| 2.7 | 清除后身份恢复 | clear 后恢复到真实身份 |
| 2.8 | Bot 重启后临权自动清除 | temppermissions 为空 |

### 群组绑定 (6 项 → 5 项待测)

| # | 命令 | 验证点 |
|---|------|--------|
| 3.1 | 非超管 `#bindgroup grp_xxx` | 应拒绝 |
| 3.2 | 非超管 `#bindgroup unbind` | 应拒绝 |
| 3.3 | 已绑定群再绑其他 | 应提示先解绑 |
| 3.4 | 未绑定群 `#bindgroup unbind` | 应提示无需解绑 |
| 3.5 | 私聊查询不同群 | `#bindgroup 750834329` vs `#bindgroup 1065673490` |

### 私聊权限限制 (5 项)

| # | 命令 | 验证点 |
|---|------|--------|
| 4.1 | 非超管私聊 `#vrclLogin` | 应拒绝 |
| 4.2 | 非超管私聊 `#2fa 123456` | 应拒绝 |
| 4.3 | 非超管私聊 `#vrcCheck` | 应拒绝 |
| 4.4 | 非超管私聊 `#instances grp_xxx` | 应拒绝 |
| 4.5 | 非超管私聊 `#whereis usr_xxx` | 应拒绝 |

### 群管理命令 (14 项)

| # | 命令 | 验证点 |
|---|------|--------|
| 5.1 | `#bot enable gmembers` → `#gmembers` | 分页显示成员列表 |
| 5.2 | `#gmembers 2` | 第二页 |
| 5.3 | `#gmembers grp_xxx 2` | 旧格式兼容：skip_grp_prefix |
| 5.4 | `#bot enable ginvite` → `#ginvite usr_xxx` | 邀请入群 |
| 5.5 | `#ginvite grp_xxx usr_xxx` | 旧格式兼容 |
| 5.6 | `#bot enable grole` → `#grole usr_xxx moderator` | 设置角色 |
| 5.7 | `#grole grp_xxx usr_xxx moderator` | 旧格式兼容 |
| 5.8 | `#grequests` | 查看入群申请 |
| 5.9 | `#gaudit` | 审核日志 |
| 5.10 | `#bot enable gban` → `#gban usr_xxx` | 二次确认 |
| 5.11 | `#bot enable gdelannounce` → `#gdelannounce ann_xxx` | 二次确认 |
| 5.12 | `#gdelannounce grp_xxx ann_xxx` | 旧格式兼容 |
| 5.13 | 未绑定群时 `#gmembers` | 应提示先绑定 |
| 5.14 | `#gannounce` 单行标题 | 应接受无正文的标题 |

### 查询命令 (3 项)

| # | 命令 | 验证点 |
|---|------|--------|
| 6.1 | `#instances` (群聊，已绑定) | 显示绑定群组实例 |
| 6.2 | 超管私聊 `#instances grp_xxx` | 正常查询 |
| 6.3 | `#instances grp_xxx` (群聊) | 参数被忽略，仍用绑定群组 |

### 命令开关与权限联动 (4 项)

| # | 命令 | 验证点 |
|---|------|--------|
| 7.1 | `#bot disable whereis` → 超管 `#whereis` | 超管也被拦 |
| 7.2 | `#bot enable whereis` → 普通用户 `#whereis` | 动态启用生效 |
| 7.3 | `#bot permission whereis 0` → 未绑定用户 `#whereis` | 权限修改生效 |
| 7.4 | `#bot reset` 后验证恢复默认 | 状态如新 |

### 边界测试 (5 项)

| # | 场景 | 验证点 |
|---|------|--------|
| 8.1 | Bot 重启后 `#bot temppermissions` | 临时权限自动清除 |
| 8.2 | `#bot settemppermission` 无 @ | 参数不足提示 |
| 8.3 | `#bot cleartemppermission` 无 @ | 参数不足提示 |
| 8.4 | `#bot permission 不存在命令 0` | 未知命令提示 |
| 8.5 | Cookie 直登 `#vrclLogin cookie=xxx` | ⚠️ 已知跨域问题 |

### 配置热重载集成测试 (7 项，需 NoneBot 运行时)

| # | 场景 | 验证点 |
|---|------|--------|
| 9.1 | 启动后 `cleanup_expired_bindings` 任务已注册 | `scheduler_service.get_task_info("cleanup_expired_bindings")` 非 None |
| 9.2 | 启动后 config_reload_service 监控已启动 | `_watcher_task` 非 None 且未 done |
| 9.3 | `auto_cleanup_enabled=false` 启动不注册任务 | 清理任务不存在 |
| 9.4 | 修改 `cleanup_interval` 后任务间隔更新 | 改为 7200 → 重载后间隔 ≈ 7200s |
| 9.5 | `auto_cleanup_enabled: false` 后任务被移除 | 重载后 `get_task_info` 返回 None |
| 9.6 | 重新启用后任务被重新注册 | false → true → 重载后任务非 None |
| 9.7 | `group_features.yml` 修改非 binding 字段 | welcome_enabled 改变，托管任务不变，但 global_config 已更新 |

### 配置热重载场景测试 (6 项，需 NoneBot 运行时)

| # | 场景 | 验证点 |
|---|------|--------|
| 10.1 | 1 秒内连续修改 3 次 YAML | 只触发 1 次重载（去抖） |
| 10.2 | 间隔 6 秒的两次修改 | 触发 2 次重载 |
| 10.3 | 写入语法错误的 YAML | 日志报错，旧配置值保留，托管任务不中断 |
| 10.4 | 监控循环内部异常不崩溃 | 日志记录后继续轮询 |
| 10.5 | 手动 `trigger_reload()` 与自动监控并发 | `_reload_lock` 保证串行 |
| 10.6 | 重载期间新任务未被提前触发 | factory 完成前不执行 |

### 配置热重载关闭链路 (2 项，需 NoneBot 运行时)

| # | 场景 | 验证点 |
|---|------|--------|
| 11.1 | shutdown 后监控 task 已 cancel | `watcher_task.cancelled() == True` |
| 11.2 | shutdown 后调度器已停止 | `scheduler.running == False` |

---

## 统计

| 状态 | 数量 |
|------|------|
| ✅ 已完成测试 | 54 (功能集成 25 + 热重载单元 29) |
| ❌ 未测试 (功能) | **44** |
| ❌ 未测试 (热重载集成/场景) | **15** |
| ⚠️ 已知问题 | 1 (Cookie 直登跨域) |

### 未测试按模块分布

| 模块 | 未测数 |
|------|--------|
| `#bot` 配置管理 | 7 |
| 临时权限 | 7 |
| 群组绑定边界 | 5 |
| 私聊限制 | 5 |
| 群管理命令 | 14 |
| 查询命令 | 3 |
| 命令开关联动 | 4 |
| 边界测试 | 5 |
| 配置热重载集成 | 7 |
| 配置热重载场景 | 6 |
| 配置热重载关闭链路 | 2 |
| 长稳/并发/多群 | 6 (未纳入计数) |

---

## 测试环境

| 项目 | 信息 |
|------|------|
| Bot QQ | ****** |
| 测试群 | ****** (****) |
| VRChat 账号 | ****** |
| VRChat ID | usr_b2d06dbd-7a37-4732-a169-a2c76ac19d22 |
| VRChat 群组 | grp_fdd4cdf6-b3e0-4be3-a040-5b8abf2617f4 (中文kipfel厅, 3975人) |
| Bot 群组角色 | 待确认（需 Owner/Mod 方可测管理命令） |
| NapCat QQ | 协议登录 |

---

## 下一步测试顺序

1. **第一阶段**（依赖前置）: `#bot enable` 各命令 → `#bot permission`
2. **第二阶段**（权限系统）: 临时权限设置 → 优先级 → 清除 → 重启清空
3. **第三阶段**（群管理）: `#gmembers` → `#grole` → `#grequests` → `#ban/kick`
4. **第四阶段**（安全边界）: 私聊拒绝 → 非超管拒绝 → 旧格式兼容
5. **第五阶段**（配置热重载集成）: 启动链路验证 → 修改 YAML 验证热重载 → 关闭链路验证
6. **第六阶段**（配置热重载场景）: 去抖 → 异常容错 → 并发重载
7. **第七阶段**（长稳）: Bot 持续运行 24h+
