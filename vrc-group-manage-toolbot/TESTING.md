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

---

## 统计

| 状态 | 数量 |
|------|------|
| ✅ 已测通过 | 25 |
| ❌ 未测试 | **44** |
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
5. **第五阶段**（长稳）: Bot 持续运行 24h+
