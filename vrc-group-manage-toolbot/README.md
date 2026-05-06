# VRC Group Manage ToolBot

基于 NoneBot2 + OneBot V11 的 QQ Bot 框架

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量

编辑 `.env` 文件,修改以下配置:

- `ONEBOT_ACCESS_TOKEN`: 你的 access token(需要与 OneBot 实现保持一致)
- `SUPERUSERS`: 超级用户 QQ 号列表,例如 `["123456789"]`
- `HOST` 和 `PORT`: Bot 运行的主机和端口

### 3. 运行 Bot

```bash
# 使用 nb-cli
nb run 
# 开发可使用重载模式
nb run --reload
```

### 4. 配置 OneBot 实现

你需要一个 OneBot v11 的实现来连接 QQ,推荐使用:
- [NapcatQQ](https://github.com/Napcat/NapcatQQ)
- [Lagrange](https://github.com/LagrangeDev/Lagrange.Core)
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- [OpenShamrock](https://github.com/whitechi73/OpenShamrock) (Android)

**重要**: 在 OneBot 实现中配置 **反向 WebSocket** 连接到:
```
ws://127.0.0.1:40796/onebot/v11/ws
```

## 项目结构

```
vrc-group-manage-toolbot/
├── bot.py              # Bot 主入口
├── run.py              # 开发启动脚本
├── .env                # 开发环境配置
├── .env.prod           # 生产环境配置
├── pyproject.toml      # 项目配置和依赖
└── plugins/            # 插件目录
    └── ...
└── utils/            # 工具目录
    └── ...
```


更多文档请参考:
- [NoneBot2 官方文档](https://nonebot.dev/)
- [OneBot V11 标准](https://github.com/botuniverse/onebot-11)

