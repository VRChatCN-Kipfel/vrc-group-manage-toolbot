# VRC Group Manage ToolBot

基于 NoneBot2 + OneBot V11 的 QQ Bot，用于通过 QQ 管理 VRChat 群组。

## 功能概览

| 模块 | 命令数 | 说明 |
|------|--------|------|
| 查询 | 2 | 用户位置、群实例 |
| 群管理 | 12 | 成员/角色/公告/审核/封禁管理 |
| 用户绑定 | 5 | QQ↔VRChat 账号绑定与查询 |
| 群组绑定 | 1 | QQ 群与 VRChat 群组绑定管理 |
| 系统 | 3 | 登录、两步验证、Cookie 直登 |

---

## 快速开始

### 1. 安装依赖

```bash
pip install nonebot2[aiohttp,fastapi,httpx,websockets] nonebot-adapter-onebot nonebot-plugin-localstore
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填写以下字段：

```ini
# VRChat API 凭据
VRC_USERNAME="你的VRChat邮箱"
VRC_PASSWORD="你的VRChat密码"

# Bot 管理员 QQ 号
SUPERUSERS=["你的QQ号"]

# 命令前缀（QQ 内 / 会被转成表情，建议用 #）
COMMAND_START=["#", "!", ""]

# Bot 昵称（用于 @Bot 触发）
NICKNAME=["Bot昵称"]
```

### 3. 启动 Bot

```bash
cd vrc-group-manage-toolbot
python run.py
```

看到 `Uvicorn running on http://127.0.0.1:40796` 即启动成功。

### 4. 配置 NapCatQQ

1. 下载 [NapCatQQ](https://github.com/NapNeko/NapCatQQ)
2. 用 Bot QQ 号扫码登录
3. 在 WebUI（`http://127.0.0.1:6099/webui`）添加反向 WebSocket：
   - 地址：`ws://127.0.0.1:40796/onebot/v11/ws`
   - Token：留空
4. 将 Bot QQ 拉入目标群聊

---

## 命令参考

### 系统命令

| 命令 | 用法 | 说明 |
|------|------|------|
| `#vrclLogin` | 直接发 | 用户名+密码登录，自动检测 2FA |
| `#2fa <验证码>` | `#2fa 123456` | 提交 TOTP 两步验证码 |
| `#vrclLogin cookie=xxx` | `#vrclLogin cookie=authcookie_xxx` | 浏览器复制 cookie 直登，跳过 2FA |
| `#vrcCheck` | 直接发 | 检查当前登录状态，不触发重认证 |

### 查询命令

| 命令 | 用法 | 说明 |
|------|------|------|
| `#whereis <用户ID>` | `#whereis usr_xxx` | 查用户在线状态和位置 |
| `#instances` | 群聊中直接发送 | 查**当前群绑定**的 VRChat 群组活跃实例 |
| `#whois @某人` | `#whois @QQ用户` | 查已绑定 QQ 用户的 VRChat 状态 |

> **注意**：`#instances` 在群聊中自动使用已绑定的 VRChat 群组，无需指定 `grp_xxx`。

### 用户绑定

| 命令 | 用法 | 权限 | 说明 |
|------|------|------|------|
| `#bind <VRC用户ID>` | `#bind usr_xxx` | 任何人 | Bio 验证码绑定（3 分钟有效） |
| `#bind force @QQ <VRCID>` | `#bind force @某人 usr_xxx` | 超管 | 跳过验证直接绑定 |
| `#confirm` | 直接发 | 任何人 | 确认 Bio 验证码，完成绑定 |
| `#unbind` | 直接发 | 已绑定用户 | 解绑（需二次确认） |
| `#bindinfo [@某人]` | `#bindinfo` | 任何人 | 查绑定状态 |

### 群组绑定（超级管理员专用）

| 命令 | 用法 | 权限 | 说明 |
|------|------|------|------|
| `#bindgroup` | 群聊中直接发送 | 任何人 | 查询当前群绑定的 VRChat 群组 |
| `#bindgroup <群ID>` | `#bindgroup grp_xxx` | 超管 | 将当前群绑定到指定 VRChat 群组 |
| `#bindgroup unbind` | 群聊中发送 | 超管 | 解除当前群的绑定 |
| `#bindgroup <群ID> <QQ号>` | 私聊中发送 | 超管 | 为指定 QQ 群绑定 VRChat 群组 |

> **重要**：所有群组管理指令都基于已绑定的 VRChat 群组，**不允许**在群聊中通过参数指定其他群组，防止越权操作。

### 群管理（需 QQ 群管理员权限 + Bot 有 VRChat 群管理权限）

| 命令 | 用法 | 说明 |
|------|------|------|
| `#gmembers [页]` | `#gmembers` 或 `#gmembers 2` | 分页查看**当前群绑定**的群组成员（20人/页） |
| `#ginvite <用户ID>` | `#ginvite usr_xxx` | 邀请用户加入**当前群绑定**的群组 |
| `#gkick <用户ID>` | `#gkick usr_xxx` | 从**当前群绑定**的群组踢出成员（二次确认） |
| `#gban <用户ID>` | `#gban usr_xxx` | 封禁**当前群绑定**的群组成员（二次确认） |
| `#gunban <用户ID>` | `#gunban usr_xxx` | 解封**当前群绑定**的群组成员 |
| `#grole <用户ID> <角色>` | `#grole usr_xxx moderator` | 为**当前群绑定**的群组设置角色（模糊匹配） |
| `#grequests` | 直接发送 | 查看**当前群绑定**的群组入群申请 |
| `#gaccept <用户ID>` | `#gaccept usr_xxx` | 批准**当前群绑定**的群组入群申请 |
| `#greject <用户ID>` | `#greject usr_xxx` | 拒绝**当前群绑定**的群组入群申请 |
| `#gannounce` | `#gannounce`<br>`标题`<br>`内容` | 在**当前群绑定**的群组发布公告（多行命令，二次确认） |
| `#gdelannounce <公告ID>` | `#gdelannounce ann_xxx` | 删除**当前群绑定**的群组公告（二次确认） |
| `#gaudit` | 直接发送 | 查看**当前群绑定**的群组审核日志（最近50条） |

> **安全策略**：所有群组管理指令在群聊中**强制使用**已绑定的 VRChat 群组，即使命令中携带 `grp_xxx` 参数也会被忽略。这确保了 QQ 群管理员只能管理当前群绑定的 VRChat 群组，防止越权操作。

### ⚙️ 配置管理（仅超级管理员）

| 命令 | 用法 | 说明 |
|------|------|------|
| `#bot` | 直接发 | 显示帮助信息 |
| `#bot status` | 直接发 | 查看当前群配置状态 |
| `#bot list` | 直接发 | 列出所有可配置命令 |
| `#bot enable <命令>` | `#bot enable gban` | 启用指定命令 |
| `#bot disable <命令>` | `#bot disable gkick` | 禁用指定命令 |
| `#bot permission <命令> <权限>` | `#bot permission whereis user` | 设置命令权限 |
| `#bot settemppermission @QQ <权限>` | `#bot settemppermission @某人 3` | 临时设定某人权限 (重启失效) |
| `#bot cleartemppermission @QQ` | `#bot cleartemppermission @某人` | 清除某人临时权限 |
| `#bot temppermissions` | 直接发 | 查看所有临时权限设置 |
| `#bot reset [命令]` | `#bot reset` 或 `#bot reset gban` | 重置配置 |

**权限等级**: 
- `0/unbound_user` - 未绑定成员
- `1/bound_user` - 已绑定成员
- `2/unbound_admin` - 未绑定管理员
- `3/bound_admin` - 已绑定管理员
- `4/owner` - 群主
- `5/superuser` - 超级管理员

详细文档请查看 [CONFIG_GUIDE.md](./CONFIG_GUIDE.md)

---

## 项目结构

```
vrc-group-manage-toolbot/
├── bot.py                  # Bot 入口
├── run.py                  # 开发启动脚本
├── pyproject.toml          # 项目配置
├── .env                    # 环境配置（不提交）
├── .env.example            # 配置模板
│
├── plugins/                # 命令插件
│   ├── group_manager.py    # 查询命令 + 登录/2FA
│   ├── group_admin.py      # 群管理命令（12个）
│   ├── user_bind.py        # 用户绑定命令（5个）
│   ├── config_manager.py   # 配置管理
│   └── group_bind.py       # 群组绑定命令
│
├── services/               # 服务层（插件 ↔ 后端）
│   ├── api_guard.py        # 速率控制 + 指数退避 + 缓存
│   ├── permission.py       # 六级权限判断
│   ├── message_utils.py    # 消息格式化/分段
│   ├── user_binding.py     # 绑定数据持久化
│   └── group_config.py     # 每群独立配置
│
├── utils/                  # 后端
│   └── VRC/
│       ├── vrc_client.py   # VRChat API HTTP 客户端
│       ├── vrc_config.py   # 配置模型
│       └── vrc_models.py   # Pydantic 数据模型
│
└── data/                   # 运行时数据（不提交）
    ├── bindings.json
    └── group_configs.json
```

---

## 安全须知

- **不要将 `.env` 提交到代码仓库**（已在 `.gitignore` 中排除）
- **使用专用 VRChat Bot 账号**，不要绑定运营者主账号
- **遵守 VRChat 使用条款**：频繁批量操作可能导致账号被封
- **Cookie 是敏感凭据**，不要在群聊中公开分享
- **BIO 验证码 3 分钟自动过期**，过时需重新绑定
- **群组绑定安全**：群聊中所有管理指令强制使用已绑定的 VRChat 群组，防止越权操作
- **私聊权限控制**：仅超级管理员可在私聊中使用 Bot，普通用户私聊会被拒绝

---

## 速率限制

所有 VRChat API 请求受以下保护：

- 最小请求间隔 1.5 秒
- 遇到 429（限速）自动指数退避重试（2s → 4s → 8s，最多 3 次）
- 401 自动提示登录，403 提示权限不足
- 查询结果默认缓存 60 秒

---

## 权限体系

### 基础权限等级

| 等级 | 身份 | 权限 |
|------|------|------|
| Lv0 | 普通 QQ 用户 | 查询、绑定、帮助 |
| Lv1 | QQ 群管理员/群主 | 群管理操作、Bot 状态 |
| Lv2 | 超级用户 (SUPERUSERS) | 强制绑定、Bot 调试、配置管理 |

### 六级权限体系（v0.2.2+）

系统现在根据 **QQ身份** 与 **VRChat绑定状态** 自动判定 6 级权限：

| 等级 | 身份描述 | 说明 |
|------|----------|------|
| Lv0 | 未绑定普通成员 | 刚进群或未绑定 VRC 账号的用户 |
| Lv1 | 已绑定普通成员 | 已完成 `/bind` 验证的活跃用户 |
| Lv2 | 未绑定管理员 | QQ 管理员但未绑定 VRC 账号 |
| Lv3 | 已绑定管理员 | QQ 管理员且已绑定 VRC 账号 |
| Lv4 | 群主 | QQ 群主（拥有最高群内管理权） |
| Lv5 | 超级管理员 | `.env` 中配置的 Bot 运营者 |

**配置示例：**
```bash
# 仅允许已绑定的管理员查看群成员
#bot permission gmembers bound_admin

# 封禁操作仅限群主执行
#bot permission gban owner
```

详见 [CONFIG_GUIDE.md](./CONFIG_GUIDE.md)

---

## 参考

- [NoneBot2 官方文档](https://nonebot.dev/)
- [OneBot V11 标准](https://github.com/botuniverse/onebot-11)
- [VRChat 社区 API 文档](https://vrchat.community)
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ)
- [CHANGELOG](./CHANGELOG.md)
