# VRC Group Manage ToolBot

基于 NoneBot2 + OneBot V11 的 QQ Bot，用于通过 QQ 管理 VRChat 群组。

## 功能概览

| 模块 | 命令数 | 说明 |
|------|--------|------|
| 查询 | 3 | 用户位置、群实例、世界信息 |
| 群管理 | 12 | 成员/角色/公告/审核/封禁管理 |
| 用户绑定 | 5 | QQ↔VRChat 账号绑定与查询 |
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
| `#instances <群ID>` | `#instances grp_xxx` | 查群组活跃实例 |
| `#whois @某人` | `#whois @QQ用户` | 查已绑定 QQ 用户的 VRChat 状态 |

### 用户绑定

| 命令 | 用法 | 权限 | 说明 |
|------|------|------|------|
| `#bind <VRC用户ID>` | `#bind usr_xxx` | 任何人 | Bio 验证码绑定（3 分钟有效） |
| `#bind force @QQ <VRCID>` | `#bind force @某人 usr_xxx` | 超管 | 跳过验证直接绑定 |
| `#confirm` | 直接发 | 任何人 | 确认 Bio 验证码，完成绑定 |
| `#unbind` | 直接发 | 已绑定用户 | 解绑（需二次确认） |
| `#bindinfo [@某人]` | `#bindinfo` | 任何人 | 查绑定状态 |

### 群管理（需 QQ 群管理员权限 + Bot 有 VRChat 群管理权限）

| 命令 | 用法 | 说明 |
|------|------|------|
| `#gmembers <群ID> [页]` | `#gmembers grp_xxx` | 分页查看群成员（20人/页） |
| `#ginvite <群ID> <用户ID>` | `#ginvite grp_xxx usr_xxx` | 邀请入群 |
| `#gkick <群ID> <用户ID>` | `#gkick grp_xxx usr_xxx` | 踢出成员（二次确认） |
| `#gban <群ID> <用户ID>` | `#gban grp_xxx usr_xxx` | 封禁成员（二次确认） |
| `#gunban <群ID> <用户ID>` | `#gunban grp_xxx usr_xxx` | 解封成员 |
| `#grole <群ID> <用户ID> <角色>` | `#grole grp_xxx usr_xxx moderator` | 设置角色（模糊匹配） |
| `#grequests <群ID>` | `#grequests grp_xxx` | 查看入群申请 |
| `#gaccept <群ID> <用户ID>` | `#gaccept grp_xxx usr_xxx` | 批准入群申请 |
| `#greject <群ID> <用户ID>` | `#greject grp_xxx usr_xxx` | 拒绝入群申请 |
| `#gannounce <群ID>\n<标题>\n<内容>` | 多行命令 | 发布公告（二次确认） |
| `#gdelannounce <群ID> <公告ID>` | `#gdelannounce grp_xxx ann_xxx` | 删除公告（二次确认） |
| `#gaudit <群ID>` | `#gaudit grp_xxx` | 查看审核日志（最近50条） |

> 设置默认群组后，所有命令可省略 `<群ID>` 参数（使用 `#bot config` 设置）。

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
│   └── user_bind.py        # 用户绑定命令（5个）
│
├── services/               # 服务层（插件 ↔ 后端）
│   ├── api_guard.py        # 速率控制 + 指数退避 + 缓存
│   ├── permission.py       # 三级权限判断
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

---

## 速率限制

所有 VRChat API 请求受以下保护：

- 最小请求间隔 1.5 秒
- 遇到 429（限速）自动指数退避重试（2s → 4s → 8s，最多 3 次）
- 401 自动提示登录，403 提示权限不足
- 查询结果默认缓存 60 秒

---

## 权限体系

| 等级 | 身份 | 权限 |
|------|------|------|
| Lv0 | 普通 QQ 用户 | 查询、绑定、帮助 |
| Lv1 | QQ 群管理员/群主 | 群管理操作、Bot 状态 |
| Lv2 | 超级用户 (SUPERUSERS) | 强制绑定、Bot 调试、热重载 |

---

## 参考

- [NoneBot2 官方文档](https://nonebot.dev/)
- [OneBot V11 标准](https://github.com/botuniverse/onebot-11)
- [VRChat 社区 API 文档](https://vrchat.community)
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ)
- [CHANGELOG](./CHANGELOG.md)
