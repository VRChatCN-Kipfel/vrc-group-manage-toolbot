# 功能开关与权限配置系统

## 📋 概述

本系统提供了细粒度的功能控制，允许超级管理员为每个QQ群单独配置：
- ✅/❌ **功能开关**：启用或禁用特定命令
- 🔐 **权限等级**：设置执行命令所需的最低权限

## 🎯 核心特性

### 1. 按群配置
每个QQ群都有独立的配置，互不影响。

### 2. 六级权限体系
| 等级 | 名称 | 说明 |
|------|------|------|
| 0 | UNBOUND_USER | 未绑定普通成员 |
| 1 | BOUND_USER | 已绑定普通成员 |
| 2 | UNBOUND_ADMIN | 未绑定管理员 |
| 3 | BOUND_ADMIN | 已绑定管理员 |
| 4 | OWNER | 群主 |
| 5 | SUPERUSER | 机器人超级管理员 |

### 3. 默认配置
所有命令都有合理的默认权限设置，开箱即用。

---

## 🔧 配置管理命令

**注意：以下命令仅超级管理员可用**

### 查看帮助
```
#bot
```

### 查看当前群配置状态
```
#bot status
```
显示：
- 基本配置（默认群组、通知等）
- 已自定义的命令配置
- 与默认配置的差异

### 列出所有可配置命令
```
#bot list
```
显示所有24个命令的当前状态和权限，标记已自定义的配置 ⚙️

### 启用命令
```
#bot enable <命令名>
```
示例：
```
#bot enable gban
```

### 禁用命令
```
#bot disable <命令名>
```
示例：
```
#bot disable gkick
```

### 设置命令权限
```
#bot permission <命令名> <权限等级>
```

权限等级可以用数字或名称：
- `0` 或 `unbound_user` - 未绑定成员
- `1` 或 `bound_user` - 已绑定成员
- `2` 或 `unbound_admin` - 未绑定管理员
- `3` 或 `bound_admin` - 已绑定管理员
- `4` 或 `owner` - 群主
- `5` 或 `superuser` - 超级管理员

示例：
```
#bot permission whereis user        # 所有人都可查询位置
#bot permission gban owner          # 仅群主可封禁
#bot permission bind 2              # 仅超管可绑定（用数字）
```

### 临时权限管理 (v0.2.3+)
**注意：以下设置仅在 Bot 本次运行期间生效，重启后自动清除。**

#### 设定临时权限
```
#bot settemppermission @QQ号 <权限等级>
```
示例：
```bash
# 紧急剥夺某管理员的权限
#bot settemppermission @捣乱的管理 0

# 临时授权某人协助管理
#bot settemppermission @热心成员 bound_admin
```

#### 查看临时权限列表
```
#bot temppermissions
```
显示当前所有被临时修改过权限的用户及其等级。

### 重置配置
```
#bot reset [命令名]
```

- 不带参数：重置所有命令为默认配置
- 带参数：重置指定命令

示例：
```
#bot reset gban           # 重置单个命令
#bot reset                # 重置所有命令
```

---

## 📊 命令分类及默认权限

### 系统/认证模块（默认：未绑定成员）
- `vrclLogin` - 登录
- `2fa` - 两步验证
- `vrcCheck` - 检查登录状态

### 查询模块（默认：已绑定成员）
- `whereis` - 查询用户位置
- `instances` - 查询群组实例
- `whois` - 查询绑定用户状态

### 用户绑定模块（默认：未绑定成员）
- `bind` - 绑定VRChat账号
- `confirm` - 确认绑定

**特殊**：`unbind`, `bindinfo` 默认需要 **已绑定成员 (Lv1)** 权限。

### 群组管理模块
- **常规管理 (默认: 已绑定管理员 Lv3)**: `gmembers`, `ginvite`, `grequests`, `gaccept`, `greject`, `gannounce`, `gaudit`
- **高危操作 (默认: 群主 Lv4)**: `gkick`, `gban`, `gunban`, `grole`, `gdelannounce`

---

## 💡 使用场景示例

### 场景1：只开放查询功能，禁用所有管理操作
```bash
# 禁用所有群组管理命令
#bot disable gmembers
#bot disable ginvite
#bot disable gkick
#bot disable gban
#bot disable gunban
#bot disable grole
#bot disable grequests
#bot disable gaccept
#bot disable greject
#bot disable gannounce
#bot disable gdelannounce
#bot disable gaudit

# 或者批量重置为更高权限（让普通人也无法使用）
#bot permission gmembers superuser
#bot permission ginvite superuser
# ... （对其他管理命令同样操作）
```

### 场景2：允许所有人使用绑定功能，但禁止解绑
```bash
#bot permission bind user      # 任何人都可绑定
#bot permission unbind admin   # 仅管理员可解绑（防止误操作）
```

### 场景3：临时禁用某个有问题的命令
```bash
#bot disable instances    # 暂时关闭实例查询
# ... 修复问题后 ...
#bot enable instances     # 重新启用
```

### 场景4：提高敏感操作的权限要求
```bash
#bot permission gban superuser      # 封禁需要超管
#bot permission gkick superuser     # 踢人需要超管
#bot permission gannounce admin     # 发布公告保持管理员权限
```

---

## 🔍 配置文件位置

配置存储在：
```
data/vrc_toolbot/group_configs.json
```

每个群的配置格式：
```json
{
  "123456789": {
    "qq_group_id": "123456789",
    "default_vrc_group": null,
    "notify_enabled": false,
    "admin_ops_enabled": true,
    "allow_user_bind": true,
    "commands": {
      "gban": {
        "enabled": true,
        "permission": 1
      },
      "whereis": {
        "enabled": false,
        "permission": 0
      }
      // ... 其他命令配置
    }
  }
}
```

**建议**：优先使用 `#bot` 命令进行配置，避免手动编辑JSON文件导致格式错误。

---

## ⚠️ 注意事项

1. **配置管理命令本身不可禁用**
   - `bot` 命令始终保持超级管理员权限
   - 无法通过 `#bot disable bot` 禁用

2. **权限检查优先级**
   - 首先检查功能是否启用
   - 然后检查用户权限等级
   - 任一条件不满足则拒绝执行

3. **force绑定特殊处理**
   - `#bind force` 始终要求超级管理员权限
   - 即使将 `bind` 权限设为 `user`，force子命令仍需要超管

4. **配置持久化**
   - 所有修改立即保存到磁盘
   - 重启Bot后配置依然有效

5. **默认值自动填充**
   - 新加入的群自动获得默认配置
   - 新增命令时自动使用默认设置

---

## 🛠️ 技术实现

### 核心组件

1. **CommandConfig** (`services/group_config.py`)
   - 单个命令的配置模型
   - 包含 `enabled` 和 `permission` 字段

2. **GroupConfig** (`services/group_config.py`)
   - 群组配置模型
   - 包含所有命令的配置字典
   - 提供便捷的读写方法

3. **check_command_permission** (`services/permission.py`)
   - 统一的权限检查函数
   - 返回 `(是否允许, 错误消息)`

4. **config_manager插件** (`plugins/config_manager.py`)
   - 提供 `#bot` 命令族
   - 仅超级管理员可访问

### 工作流程

```
用户发送命令
    ↓
插件handler接收
    ↓
调用 check_command_permission(bot, event, command_name)
    ↓
获取群组配置 → 检查enabled → 检查permission
    ↓
返回 (True, "") 或 (False, "错误消息")
    ↓
根据结果继续执行或终止
```

---

## 📝 扩展指南

### 添加新命令

1. 在 `COMMAND_DEFAULTS` 中添加默认配置：
```python
COMMAND_DEFAULTS = {
    # ... 现有命令 ...
    "newcommand": {"enabled": True, "permission": PermissionLevel.USER},
}
```

2. 在插件中使用权限检查：
```python
@new_cmd.handle()
async def handle_new(bot: Bot, event: GroupMessageEvent):
    allowed, error_msg = await check_command_permission(bot, event, "newcommand")
    if not allowed:
        await new_cmd.finish(error_msg)
    
    # ... 正常逻辑 ...
```

3. 更新文档和测试

---

## ❓ 常见问题

**Q: 如何快速查看所有被禁用的命令？**
A: 使用 `#bot status`，会列出所有与默认配置不同的命令。

**Q: 配置错了怎么办？**
A: 使用 `#bot reset` 重置所有配置，或 `#bot reset <命令>` 重置单个命令。

**Q: 能否为不同用户设置不同权限？**
A: 目前只支持基于角色的权限（普通用户/群管理/超管），不支持针对单个用户的权限设置。

**Q: 配置会影响所有群吗？**
A: 不会，每个群有独立的配置。

**Q: 如何备份配置？**
A: 直接复制 `data/vrc_toolbot/group_configs.json` 文件即可。
