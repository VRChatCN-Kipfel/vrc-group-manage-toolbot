# 定时任务调度器使用指南

本文档介绍如何在项目中使用 `SchedulerService` 来管理定时任务。

## 目录

- [简介](#简介)
- [基本用法](#基本用法)
  - [间隔任务](#间隔任务)
  - [Cron 表达式任务](#cron-表达式任务)
  - [一次性任务](#一次性任务)
- [任务管理](#任务管理)
  - [查看任务列表](#查看任务列表)
  - [查看任务详情](#查看任务详情)
  - [暂停/恢复任务](#暂停恢复任务)
  - [移除任务](#移除任务)
  - [修改任务](#修改任务)
- [调度器控制](#调度器控制)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 简介

`SchedulerService` 是基于 `nonebot-plugin-apscheduler` 封装的定时任务调度服务，提供了统一的接口来管理各种类型的定时任务。

### 主要特性

- ✅ 支持间隔执行任务（Interval）
- ✅ 支持 Cron 表达式任务
- ✅ 支持一次性定时任务（Date）
- ✅ 提供完整的任务管理功能（查看、暂停、恢复、删除、修改）
- ✅ 自动日志记录
- ✅ 任务 ID 唯一性管理

## 基本用法

### 导入服务

```python
from services.scheduler_service import scheduler_service
```

### 间隔任务

间隔任务会按照固定的时间间隔重复执行。

#### 示例：每 10 秒执行一次

```python
async def demo_periodic_task():
    """这是一个每 10 秒执行一次的演示任务"""
    logger.info("🕒 定时任务触发: 正在执行演示任务...")
    # 在这里可以放置你的业务逻辑，比如检查 API 状态、清理缓存等

# 注册间隔任务
scheduler_service.add_interval_task(
    func=demo_periodic_task,
    seconds=10,
    task_id="demo_task_10s"
)
```

#### 参数说明

- `func`: 要执行的异步函数
- `seconds`: 间隔秒数
- `minutes`: 间隔分钟数
- `hours`: 间隔小时数
- `task_id`: 任务唯一标识符（可选，默认为函数名）

#### 更多示例

```python
# 每 5 分钟执行一次
scheduler_service.add_interval_task(
    func=my_function,
    minutes=5,
    task_id="check_api_status"
)

# 每小时执行一次
scheduler_service.add_interval_task(
    func=my_function,
    hours=1,
    task_id="hourly_cleanup"
)

# 每 30 秒执行一次
scheduler_service.add_interval_task(
    func=my_function,
    seconds=30,
    task_id="frequent_check"
)
```

### Cron 表达式任务

Cron 任务允许你使用标准的 Cron 表达式来定义任务的执行时间。

#### 示例：每天凌晨 2:30 执行

```python
async def demo_cron_task():
    """这是一个每天凌晨执行的演示任务"""
    logger.info("🌅 Cron 定时任务触发: 正在执行每日清理任务...")
    await asyncio.sleep(1)
    logger.info("✅ 每日清理任务完成")

# 注册 Cron 任务：每天凌晨 2:30 执行
scheduler_service.add_cron_task(
    func=demo_cron_task,
    cron_expr="30 2 * * *",  # 分 时 日 月 星期
    task_id="demo_cron_daily"
)
```

#### Cron 表达式格式

Cron 表达式由 5 个字段组成，用空格分隔：

```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日期 (1 - 31)
│ │ │ ┌───────────── 月份 (1 - 12)
│ │ │ │ ┌───────────── 星期 (0 - 6, 0 表示星期日)
│ │ │ │ │
* * * * *
```

#### 常用 Cron 表达式示例

```python
# 每天早上 8:00 执行
scheduler_service.add_cron_task(
    func=my_function,
    cron_expr="0 8 * * *",
    task_id="morning_task"
)

# 每周一上午 9:00 执行
scheduler_service.add_cron_task(
    func=my_function,
    cron_expr="0 9 * * 1",
    task_id="weekly_monday_task"
)

# 每月 1 号凌晨 0:00 执行
scheduler_service.add_cron_task(
    func=my_function,
    cron_expr="0 0 1 * *",
    task_id="monthly_task"
)

# 工作日（周一至周五）下午 6:00 执行
scheduler_service.add_cron_task(
    func=my_function,
    cron_expr="0 18 * * 1-5",
    task_id="weekday_evening_task"
)

# 每小时的第 30 分钟执行
scheduler_service.add_cron_task(
    func=my_function,
    cron_expr="30 * * * *",
    task_id="half_hourly_task"
)
```

### 一次性任务

一次性任务会在指定的时间点执行一次，然后自动移除。

#### 示例：5 分钟后执行

```python
from datetime import datetime, timedelta

async def demo_one_time_task():
    """这是一个一次性执行的演示任务"""
    logger.info("⏰ 一次性任务触发: 执行特定时间的任务")
    await asyncio.sleep(1)
    logger.info("✅ 一次性任务完成")

# 注册一次性任务：5分钟后执行
run_time = datetime.now() + timedelta(minutes=5)
scheduler_service.add_date_task(
    func=demo_one_time_task,
    run_date=run_time,
    task_id="demo_one_time_task"
)
```

#### 参数说明

- `func`: 要执行的异步函数
- `run_date`: 执行时间（datetime 对象）
- `task_id`: 任务唯一标识符（可选，默认为函数名）

#### 更多示例

```python
# 在指定日期时间执行
specific_time = datetime(2024, 12, 25, 0, 0, 0)  # 2024年12月25日 00:00:00
scheduler_service.add_date_task(
    func=my_function,
    run_date=specific_time,
    task_id="christmas_task"
)

# 1 小时后执行
one_hour_later = datetime.now() + timedelta(hours=1)
scheduler_service.add_date_task(
    func=my_function,
    run_date=one_hour_later,
    task_id="one_hour_task"
)
```

## 任务管理

### 查看任务列表

获取当前所有正在运行的任务。

```python
jobs = scheduler_service.get_all_jobs()

for job in jobs:
    print(f"任务ID: {job.id}")
    print(f"下次执行: {job.next_run_time}")
    print("-" * 20)
```

#### 命令示例

在聊天机器人中，可以使用 `/tasks` 命令查看所有任务：

```python
@show_tasks.handle()
async def handle_show_tasks(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await show_tasks.finish("❌ 仅超级管理员可查看任务列表")

    jobs = scheduler_service.get_all_jobs()
    
    if not jobs:
        await show_tasks.finish("✨ 当前没有运行中的定时任务")

    msg = "📋 当前运行的定时任务:\n" + "=" * 30 + "\n"
    for job in jobs:
        msg += f"ID: {job.id}\n"
        msg += f"下次执行: {job.next_run_time}\n"
        msg += "-" * 20 + "\n"

    await show_tasks.finish(msg)
```

### 查看任务详情

获取指定任务的详细信息。

```python
info = scheduler_service.get_task_info("demo_task_10s")

if info:
    print(f"ID: {info['id']}")
    print(f"名称: {info['name']}")
    print(f"触发器: {info['trigger']}")
    print(f"下次执行: {info['next_run_time']}")
    print(f"函数: {info['func']}")
else:
    print("任务不存在")
```

#### 命令示例

```python
@task_info.handle()
async def handle_task_info(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await task_info.finish("❌ 仅超级管理员可查看任务信息")

    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await task_info.finish("❌ 请提供任务ID，例如: /task_info demo_task_10s")
    
    task_id = args[1]
    info = scheduler_service.get_task_info(task_id)
    
    if info:
        msg = f"📊 任务信息:\n"
        msg += f"ID: {info['id']}\n"
        msg += f"名称: {info['name']}\n"
        msg += f"触发器: {info['trigger']}\n"
        msg += f"下次执行: {info['next_run_time']}\n"
        msg += f"函数: {info['func']}\n"
        await task_info.finish(msg)
    else:
        await task_info.finish(f"❌ 未找到任务: {task_id}")
```

### 暂停/恢复任务

#### 暂停任务

```python
scheduler_service.pause_task("demo_task_10s")
```

#### 恢复任务

```python
scheduler_service.resume_task("demo_task_10s")
```

#### 命令示例

```python
# 暂停任务
@pause_task_cmd.handle()
async def handle_pause_task(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await pause_task_cmd.finish("❌ 仅超级管理员可暂停任务")

    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await pause_task_cmd.finish("❌ 请提供任务ID，例如: /pause_task demo_task_10s")
    
    task_id = args[1]
    scheduler_service.pause_task(task_id)
    await pause_task_cmd.finish(f"⏸️ 已尝试暂停任务: {task_id}")

# 恢复任务
@resume_task_cmd.handle()
async def handle_resume_task(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await resume_task_cmd.finish("❌ 仅超级管理员可恢复任务")

    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await resume_task_cmd.finish("❌ 请提供任务ID，例如: /resume_task demo_task_10s")
    
    task_id = args[1]
    scheduler_service.resume_task(task_id)
    await resume_task_cmd.finish(f"▶️ 已尝试恢复任务: {task_id}")
```

### 移除任务

永久删除一个任务。

```python
scheduler_service.remove_task("demo_task_10s")
```

#### 命令示例

```python
@remove_task_cmd.handle()
async def handle_remove_task(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await remove_task_cmd.finish("❌ 仅超级管理员可移除任务")

    message = str(event.get_message()).strip()
    args = message.split(maxsplit=1)
    
    if len(args) < 2:
        await remove_task_cmd.finish("❌ 请提供任务ID，例如: /remove_task demo_task_10s")
    
    task_id = args[1]
    scheduler_service.remove_task(task_id)
    await remove_task_cmd.finish(f"🗑️ 已尝试移除任务: {task_id}")
```

### 修改任务

动态修改任务的参数（如触发器、执行函数等）。

```python
# 修改任务的执行间隔
scheduler_service.modify_task(
    "demo_task_10s",
    trigger=IntervalTrigger(seconds=30)  # 改为每 30 秒执行
)
```

## 调度器控制

### 检查调度器状态

```python
is_running = scheduler_service.is_scheduler_running()
if is_running:
    print("调度器正在运行")
else:
    print("调度器已停止")
```

#### 命令示例

```python
@scheduler_status.handle()
async def handle_scheduler_status(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await scheduler_status.finish("❌ 仅超级管理员可查看调度器状态")

    is_running = scheduler_service.is_scheduler_running()
    status = "🟢 运行中" if is_running else "🔴 已停止"
    await scheduler_status.finish(f"调度器状态: {status}")
```

### 手动启动/关闭调度器

通常情况下，调度器会随着 NoneBot2 应用自动启动和关闭。但在某些特殊场景下，你可能需要手动控制。

```python
# 启动调度器
scheduler_service.start_scheduler()

# 关闭调度器
scheduler_service.shutdown_scheduler()
```

> ⚠️ **注意**：手动控制调度器通常不需要，除非你有特殊的部署需求。

## 最佳实践

### 1. 任务函数应该是异步的

所有的任务函数都应该使用 `async def` 定义，以支持异步操作：

```python
async def my_task():
    # 执行异步操作
    await some_async_function()
```

### 2. 使用有意义的任务 ID

为每个任务设置唯一的、有意义的 ID，便于管理和调试：

```python
# ✅ 好的做法
scheduler_service.add_interval_task(
    func=check_api_health,
    minutes=5,
    task_id="api_health_check"
)

# ❌ 避免使用默认 ID
scheduler_service.add_interval_task(
    func=check_api_health,
    minutes=5
)
```

### 3. 添加错误处理

在任务函数中添加适当的错误处理，避免任务失败影响其他任务：

```python
async def my_task():
    try:
        logger.info("开始执行任务...")
        # 你的业务逻辑
        await do_something()
        logger.info("任务执行成功")
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
```

### 4. 合理使用日志

在任务的关键节点添加日志，便于追踪和调试：

```python
async def cleanup_task():
    logger.info("🧹 开始执行清理任务")
    
    try:
        # 清理逻辑
        count = await clean_old_records()
        logger.info(f"✅ 清理完成，共清理 {count} 条记录")
    except Exception as e:
        logger.error(f"❌ 清理任务失败: {e}")
```

### 5. 避免长时间运行的任务

如果任务可能需要较长时间执行，考虑使用后台任务或队列：

```python
async def long_running_task():
    # 对于耗时操作，考虑使用其他方式
    # 而不是阻塞调度器
    asyncio.create_task(process_large_dataset())
```

### 6. 任务幂等性

确保任务可以安全地重复执行（幂等性），特别是在网络请求或数据库操作中：

```python
async def sync_data():
    # 确保即使重复执行也不会产生副作用
    await sync_if_needed()
```

### 7. 权限控制

对于管理命令，始终添加权限检查：

```python
@command.handle()
async def handle_command(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await command.finish("❌ 权限不足")
    
    # 执行操作
```

## 常见问题

### Q1: 任务没有执行怎么办？

**检查清单：**

1. 确认调度器正在运行：`scheduler_service.is_scheduler_running()`
2. 检查任务是否正确注册：`scheduler_service.get_all_jobs()`
3. 查看日志中是否有错误信息
4. 确认任务函数是异步的（使用 `async def`）
5. 检查任务是否被意外暂停

### Q2: 如何调试定时任务？

**方法：**

1. 使用 `/tasks` 命令查看任务列表
2. 使用 `/task_info <task_id>` 查看任务详情
3. 在任务函数中添加详细的日志输出
4. 暂时将间隔时间调短进行测试
5. 使用一次性任务测试特定时间的执行

### Q3: 任务执行失败会影响其他任务吗？

不会。每个任务是独立执行的，一个任务的失败不会影响其他任务的执行。但建议在任务中添加错误处理和日志记录。

### Q4: 如何在运行时动态添加任务？

你可以在任何地方调用 `scheduler_service` 的方法来添加任务：

```python
# 在命令处理函数中动态添加任务
@add_task.handle()
async def handle_add_task(bot: Bot, event: MessageEvent):
    async def dynamic_task():
        logger.info("动态添加的任务执行了")
    
    scheduler_service.add_interval_task(
        func=dynamic_task,
        minutes=1,
        task_id=f"dynamic_task_{int(time.time())}"
    )
    await add_task.finish("✅ 任务已添加")
```

### Q5: 重启后任务会保留吗？

默认情况下，任务是在代码中注册的，重启后会重新注册。如果你需要持久化任务配置，建议：

1. 将任务配置存储在配置文件或数据库中
2. 在应用启动时从配置中读取并注册任务
3. 或者使用 APScheduler 的作业存储功能（需要额外配置）

### Q6: Cron 表达式不正确怎么办？

确保 Cron 表达式格式正确：

- 必须是 5 个字段：`分 时 日 月 星期`
- 每个字段的值必须在有效范围内
- 可以使用在线 Cron 表达式验证工具进行测试

常见错误：

```python
# ❌ 错误：只有 4 个字段
"30 2 * *"

# ❌ 错误：分钟值超出范围
"60 2 * * *"

# ✅ 正确
"30 2 * * *"
```

## 完整示例

以下是一个完整的插件示例，展示了各种任务类型的使用：

```python
"""
完整的定时任务示例插件
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from services.scheduler_service import scheduler_service
from services.permission import get_permission_level, PermissionLevel
import asyncio
from datetime import datetime, timedelta


# ========== 任务定义 ==========

async def health_check_task():
    """API 健康检查任务"""
    logger.info("🔍 执行 API 健康检查...")
    try:
        # 模拟 API 检查
        await asyncio.sleep(1)
        logger.info("✅ API 健康检查通过")
    except Exception as e:
        logger.error(f"❌ API 健康检查失败: {e}")


async def daily_report_task():
    """每日报告生成任务"""
    logger.info("📊 生成每日报告...")
    try:
        await asyncio.sleep(2)
        logger.info("✅ 每日报告生成完成")
    except Exception as e:
        logger.error(f"❌ 每日报告生成失败: {e}")


async def cache_cleanup_task():
    """缓存清理任务"""
    logger.info("🧹 清理过期缓存...")
    try:
        await asyncio.sleep(1)
        logger.info("✅ 缓存清理完成")
    except Exception as e:
        logger.error(f"❌ 缓存清理失败: {e}")


# ========== 任务注册 ==========

# 每 5 分钟执行一次健康检查
scheduler_service.add_interval_task(
    func=health_check_task,
    minutes=5,
    task_id="api_health_check"
)

# 每天凌晨 3:00 生成每日报告
scheduler_service.add_cron_task(
    func=daily_report_task,
    cron_expr="0 3 * * *",
    task_id="daily_report"
)

# 每小时清理一次缓存
scheduler_service.add_cron_task(
    func=cache_cleanup_task,
    cron_expr="0 * * * *",
    task_id="cache_cleanup"
)


# ========== 管理命令 ==========

show_tasks = on_command("tasks", priority=5)

@show_tasks.handle()
async def handle_show_tasks(bot: Bot, event: MessageEvent):
    level = await get_permission_level(bot, event)
    if level < PermissionLevel.SUPERUSER:
        await show_tasks.finish("❌ 仅超级管理员可查看任务列表")

    jobs = scheduler_service.get_all_jobs()
    
    if not jobs:
        await show_tasks.finish("✨ 当前没有运行中的定时任务")

    msg = "📋 当前运行的定时任务:\n" + "=" * 30 + "\n"
    for job in jobs:
        msg += f"ID: {job.id}\n"
        msg += f"下次执行: {job.next_run_time}\n"
        msg += "-" * 20 + "\n"

    await show_tasks.finish(msg)
```

*如有任何问题，请查看日志输出或使用管理命令进行调试。*
