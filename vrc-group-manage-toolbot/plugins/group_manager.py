"""
群组实例管理插件
提供查询群组实例、用户状态等功能
"""

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from nonebot.params import CommandArg
from nonebot.rule import to_me

from utils import VRC


# 创建命令处理器
group_instances = on_command("instances", rule=to_me(), priority=5)
user_location = on_command("whereis", rule=to_me(), priority=5)


# 全局客户端实例（单例模式）
_vrc_client: VRC.VRCClient = None


def get_vrc_client() -> VRC.VRCClient:
    """获取 VRChat 客户端实例（单例）"""
    global _vrc_client
    if _vrc_client is None:
        config = VRC.VRCConfig.from_env()
        _vrc_client = VRC.VRCClient(config)
    return _vrc_client


@group_instances.handle()
async def handle_group_instances(bot: Bot, event: MessageEvent, args: MessageEvent = CommandArg()):
    """
    查询群组的活跃实例
    用法: /instances <group_id>
    """
    group_id = args.extract_plain_text().strip()
    
    if not group_id:
        await group_instances.finish("请提供群组 ID\n用法: /instances grp_xxx")
    
    await group_instances.send("正在查询群组实例...")
    
    try:
        client = get_vrc_client()
        
        # 获取群组信息
        group = await client.get_group(group_id)
        if not group:
            await group_instances.finish(f"无法获取群组信息: {group_id}")
        
        # 获取群组的活跃实例
        instances = await client.get_group_instances(group_id)
        
        if not instances:
            msg = f"群组: {group.name}\n当前没有活跃实例"
            await group_instances.finish(msg)
        
        # 构建回复消息
        msg = f"群组: {group.name}\n"
        msg += f"成员数: {group.memberCount or 'N/A'}\n"
        msg += f"在线成员: {group.onlineMemberCount or 'N/A'}\n\n"
        msg += f"活跃实例 ({len(instances)}个):\n\n"
        
        for i, inst in enumerate(instances[:10], 1):  # 最多显示10个
            msg += f"{i}. {inst.worldName or '未知世界'}\n"
            msg += f"   人数: {inst.userCount}/{inst.capacity}\n"
            msg += f"   区域: {inst.region or 'N/A'}\n"
            msg += f"   类型: {inst.groupAccessType or 'N/A'}\n\n"
        
        if len(instances) > 10:
            msg += f"... 还有 {len(instances) - 10} 个实例"
        
        await group_instances.finish(msg)
        
    except Exception as e:
        logger.error(f"查询群组实例失败: {e}")
        await group_instances.finish(f"查询失败: {str(e)}")


@user_location.handle()
async def handle_user_location(bot: Bot, event: MessageEvent, args: MessageEvent = CommandArg()):
    """
    查询用户当前位置
    用法: /whereis <user_id>
    """
    user_id = args.extract_plain_text().strip()
    
    if not user_id:
        await user_location.finish("请提供用户 ID\n用法: /whereis usr_xxx")
    
    await user_location.send("正在查询用户位置...")
    
    try:
        client = get_vrc_client()
        
        # 获取用户信息
        user = await client.get_user(user_id)
        if not user:
            await user_location.finish(f"无法获取用户信息: {user_id}")
        
        # 构建回复消息
        msg = f"用户: {user.displayName}\n"
        msg += f"状态: {user.status or '离线'}\n"
        
        if user.location:
            msg += f"位置: {user.location}\n"
            
            # 如果在实例中，尝试获取实例详情
            if ":" in user.location:
                await user_location.send("正在获取实例详情...")
                
                # 解析实例 ID
                location_parts = user.location.split(":")
                if len(location_parts) >= 2:
                    world_id = location_parts[0]
                    instance_tag = location_parts[1].split("~")[0]
                    instance_id = f"{world_id}:{instance_tag}"
                    
                    instance = await client.get_instance(instance_id)
                    if instance:
                        msg += f"世界: {instance.worldName or '未知'}\n"
                        msg += f"区域: {instance.region or 'N/A'}\n"
                        msg += f"人数: {instance.userCount}/{instance.capacity}\n"
        else:
            msg += "位置: 离线或隐藏"
        
        await user_location.finish(msg)
        
    except Exception as e:
        logger.error(f"查询用户位置失败: {e}")
        await user_location.finish(f"查询失败: {str(e)}")


# 可选：添加一个登录命令用于测试
vrc_login = on_command("vrclLogin", rule=to_me(), priority=5)


@vrc_login.handle()
async def handle_vrc_login(bot: Bot, event: MessageEvent):
    """
    登录 VRChat API（测试用）
    用法: /vrclLogin
    """
    await vrc_login.send("正在登录 VRChat API...")
    
    try:
        client = get_vrc_client()
        
        # 尝试登录
        success = await client.login()
        
        if success:
            user = await client.get_current_user()
            if user:
                await vrc_login.finish(f"登录成功！欢迎, {user.displayName}")
            else:
                await vrc_login.finish("登录成功但无法获取用户信息")
        else:
            await vrc_login.finish("登录失败，请检查 .env 中的配置")
        
    except Exception as e:
        logger.error(f"VRChat 登录失败: {e}")
        await vrc_login.finish(f"登录失败: {str(e)}")
