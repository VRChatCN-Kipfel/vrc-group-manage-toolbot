from enum import IntEnum
from typing import TYPE_CHECKING, Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path

from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from nonebot_plugin_localstore import get_data_dir

if TYPE_CHECKING:
    from utils import VRCClient


class PermissionLevel(IntEnum):
    BANNED_USER = -1      # 被封禁用户
    UNBOUND_USER = 0      # 未绑定普通成员
    BOUND_USER = 1        # 已绑定普通成员
    UNBOUND_ADMIN = 2     # 未绑定管理员
    BOUND_ADMIN = 3       # 已绑定管理员
    OWNER = 4             # 群主
    SUPERUSER = 5         # 机器人超级管理员
    
    @classmethod
    def from_str(cls, level_str: str) -> "PermissionLevel":
        """从字符串转换为权限等级"""
        mapping = {
            "banned": cls.BANNED_USER, "-1": cls.BANNED_USER,
            "unbound_user": cls.UNBOUND_USER, "0": cls.UNBOUND_USER,
            "bound_user": cls.BOUND_USER, "1": cls.BOUND_USER,
            "unbound_admin": cls.UNBOUND_ADMIN, "2": cls.UNBOUND_ADMIN,
            "bound_admin": cls.BOUND_ADMIN, "3": cls.BOUND_ADMIN,
            "owner": cls.OWNER, "4": cls.OWNER,
            "superuser": cls.SUPERUSER, "5": cls.SUPERUSER,
        }
        return mapping[level_str.strip().lower()]


# 临时权限存储: {qq_id: PermissionLevel}
_temp_permissions: Dict[str, PermissionLevel] = {}


# ==================== 黑名单持久化存储 ====================

class BlacklistStore:
    """黑名单持久化存储管理器"""
    
    def __init__(self):
        self.data_dir = get_data_dir("vrc_toolbot")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.blacklist_file = self.data_dir / "blacklist.json"
        self.blacklist: Dict[str, dict] = {}  # {qq_id: ban_info}
        self._load()
    
    def _load(self):
        """从文件加载黑名单数据"""
        if self.blacklist_file.exists():
            try:
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.blacklist = data.get("banned_users", {})
                logger.info(f"已加载 {len(self.blacklist)} 条黑名单记录")
            except Exception as e:
                logger.error(f"加载黑名单失败: {e}")
                self.blacklist = {}
        else:
            logger.info("黑名单文件不存在，创建新的黑名单")
            self.blacklist = {}
            self._save()
    
    def _save(self):
        """保存黑名单数据到文件"""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "banned_users": self.blacklist
            }
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("黑名单数据已保存")
        except Exception as e:
            logger.error(f"保存黑名单失败: {e}")
    
    def add_ban(
        self,
        banned_qq: str,
        banned_by: str,
        reason: str = "未说明",
        group_id: Optional[str] = None,
        group_name: Optional[str] = None,
        message_context: Optional[str] = None,
        ban_type: str = "manual"  # manual/auto/expired
    ) -> bool:
        """
        添加用户到黑名单
        
        Args:
            banned_qq: 被封禁的 QQ 号
            banned_by: 执行封禁的操作者 QQ 号
            reason: 封禁原因
            group_id: 封禁发生的群 ID（可选）
            group_name: 封禁发生的群名称（可选）
            message_context: 触发封禁的消息上下文（可选）
            ban_type: 封禁类型 (manual/auto/expired)
        
        Returns:
            是否成功添加
        """
        banned_qq = str(banned_qq)
        banned_by = str(banned_by)
        
        ban_info = {
            "banned_qq": banned_qq,
            "banned_by": banned_by,
            "reason": reason,
            "group_id": group_id,
            "group_name": group_name,
            "message_context": message_context,
            "ban_type": ban_type,
            "banned_at": datetime.now().isoformat(),
            "expires_at": None,  # 可以扩展为临时封禁
            "status": "active"  # active/removed/expired
        }
        
        self.blacklist[banned_qq] = ban_info
        self._save()
        logger.info(f"已将 {banned_qq} 加入黑名单，操作者: {banned_by}, 原因: {reason}")
        return True
    
    def remove_ban(self, qq_id: str, removed_by: str, reason: str = "未说明") -> bool:
        """
        从黑名单移除用户
        
        Args:
            qq_id: 要解封的 QQ 号
            removed_by: 执行解封的操作者 QQ 号
            reason: 解封原因
        
        Returns:
            是否成功移除
        """
        qq_id = str(qq_id)
        
        if qq_id not in self.blacklist:
            logger.warning(f"QQ {qq_id} 不在黑名单中")
            return False
        
        # 保留历史记录，标记为 removed
        ban_info = self.blacklist[qq_id]
        ban_info["status"] = "removed"
        ban_info["removed_by"] = str(removed_by)
        ban_info["removed_at"] = datetime.now().isoformat()
        ban_info["remove_reason"] = reason
        
        # 也可以选择完全删除：del self.blacklist[qq_id]
        # 这里选择保留历史，但标记为非活跃
        self._save()
        logger.info(f"已将 {qq_id} 从黑名单移除，操作者: {removed_by}")
        return True
    
    def is_blacklisted(self, qq_id: str) -> bool:
        """检查用户是否在黑名单中（仅检查活跃状态）"""
        qq_id = str(qq_id)
        if qq_id not in self.blacklist:
            return False
        return self.blacklist[qq_id].get("status") == "active"
    
    def get_ban_info(self, qq_id: str) -> Optional[dict]:
        """获取用户的封禁详细信息"""
        qq_id = str(qq_id)
        return self.blacklist.get(qq_id)
    
    def get_all_bans(self, active_only: bool = True) -> List[dict]:
        """
        获取所有黑名单记录
        
        Args:
            active_only: 是否只返回活跃状态的封禁
        
        Returns:
            封禁记录列表
        """
        if active_only:
            return [
                info for info in self.blacklist.values()
                if info.get("status") == "active"
            ]
        return list(self.blacklist.values())
    
    def get_ban_count(self, active_only: bool = True) -> int:
        """获取黑名单用户数量"""
        return len(self.get_all_bans(active_only))


# 全局黑名单存储实例
blacklist_store = BlacklistStore()


from .global_config import global_config

async def get_permission_level(bot: Bot, event: MessageEvent) -> PermissionLevel:
    from .user_binding import user_binding_store
    
    user_id = event.user_id
    sender = event.sender
    qq_id = str(user_id)
    
    # -1. 检查是否在黑名单中（最高优先级，受全局配置控制）
    if global_config.is_blacklist_enabled and blacklist_store.is_blacklisted(qq_id):
        return PermissionLevel.BANNED_USER
    
    # 0. 检查是否有临时设定的权限 (优先级最高)
    temp = _temp_permissions.get(qq_id)
    if temp is not None:
        return temp
    
    # 1. 检查是否为机器人超管 (Lv5)
    if qq_id in bot.config.superusers:
        return PermissionLevel.SUPERUSER
    
    # 2. 私聊事件：只能是超管或普通用户
    if isinstance(event, PrivateMessageEvent):
        # 私聊中没有群角色概念，返回未绑定用户或已绑定用户
        binding = user_binding_store.get_by_qq(qq_id)
        if binding and binding.confirmed:
            return PermissionLevel.BOUND_USER
        else:
            return PermissionLevel.UNBOUND_USER
    
    # 3. 群聊事件：检查群角色
    sender_role = getattr(sender, 'role', None)
    if sender_role == "owner":
        return PermissionLevel.OWNER
    
    # 4. 检查是否为管理员 (Lv2 or Lv3)
    if sender_role == "admin":
        # 检查是否已绑定
        binding = user_binding_store.get_by_qq(qq_id)
        if binding and binding.confirmed:
            return PermissionLevel.BOUND_ADMIN
        else:
            return PermissionLevel.UNBOUND_ADMIN
    
    # 5. 检查普通成员 (Lv0 or Lv1)
    binding = user_binding_store.get_by_qq(qq_id)
    if binding and binding.confirmed:
        return PermissionLevel.BOUND_USER
    else:
        return PermissionLevel.UNBOUND_USER


def set_temp_permission(qq_id: str, level: PermissionLevel):
    """设置临时权限（仅本次运行生效）"""
    _temp_permissions[str(qq_id)] = level


def clear_temp_permission(qq_id: str):
    """清除临时权限"""
    _temp_permissions.pop(str(qq_id), None)


def get_all_temp_permissions() -> Dict[str, PermissionLevel]:
    """获取所有临时权限设置"""
    return _temp_permissions.copy()


async def check_vrc_group_role(
    vrc_client: "VRCClient",
    user_id: str,
    group_id: str,
    required_roles: Optional[list] = None,
) -> bool:
    if required_roles is None:
        required_roles = ["owner", "moderator"]

    try:
        member = await vrc_client.get_group_member(group_id, user_id)
        if not member or not member.roleIds:
            return False

        roles = await vrc_client.get_group_roles(group_id)
        role_map = {r.id: r for r in roles}

        for role_id in member.roleIds:
            role = role_map.get(role_id)
            if role and role.name.lower() in required_roles:
                return True
        return False
    except Exception as e:
        logger.warning(f"check_vrc_group_role failed: {e}")
        return False


async def check_command_permission(
    bot: Bot,
    event: MessageEvent,
    command_name: str,
    required_level: Optional[PermissionLevel] = None,
) -> tuple[bool, str]:
    """
    检查用户是否有权限执行指定命令
    
    Args:
        bot: Bot实例
        event: 事件对象（可以是群聊或私聊）
        command_name: 命令名称
        required_level: 要求的最低权限等级（如果为None则从配置中读取）
    
    Returns:
        (是否有权限, 错误消息)
    """
    from .group_config import group_config_store
    
    # 私聊事件：不使用群组配置，直接检查权限等级
    if isinstance(event, PrivateMessageEvent):
        user_level = await get_permission_level(bot, event)
        
        # 如果未指定required_level，使用默认最低权限
        if required_level is None:
            from .group_config import COMMAND_DEFAULTS
            defaults = COMMAND_DEFAULTS.get(command_name, {})
            required_level = defaults.get("permission", PermissionLevel.UNBOUND_USER)
        
        # 检查权限等级
        if user_level < required_level:
            level_names = {
                PermissionLevel.BANNED_USER: "被封禁用户",
                PermissionLevel.UNBOUND_USER: "未绑定成员",
                PermissionLevel.BOUND_USER: "已绑定成员",
                PermissionLevel.UNBOUND_ADMIN: "未绑定管理员",
                PermissionLevel.BOUND_ADMIN: "已绑定管理员",
                PermissionLevel.OWNER: "群主",
                PermissionLevel.SUPERUSER: "超级管理员",
            }
            return False, f"❌ 权限不足：需要{level_names.get(required_level, '未知')}权限"
        
        return True, ""
    
    # 群聊事件：使用群组配置
    config = group_config_store.get(str(event.group_id))
    
    # 获取用户的权限等级
    user_level = await get_permission_level(bot, event)
    
    # 如果未指定required_level，从配置中读取
    if required_level is None:
        required_level = config.get_command_permission(command_name)
    
    # 检查功能是否启用
    if not config.is_command_enabled(command_name):
        return False, f"❌ 命令 #{command_name} 在此群已被禁用"
    
    # 检查权限等级
    if user_level < required_level:
        level_names = {
            PermissionLevel.BANNED_USER: "被封禁用户",
            PermissionLevel.UNBOUND_USER: "未绑定成员",
            PermissionLevel.BOUND_USER: "已绑定成员",
            PermissionLevel.UNBOUND_ADMIN: "未绑定管理员",
            PermissionLevel.BOUND_ADMIN: "已绑定管理员",
            PermissionLevel.OWNER: "群主",
            PermissionLevel.SUPERUSER: "超级管理员",
        }
        return False, f"❌ 权限不足：需要{level_names.get(required_level, '未知')}权限"
    
    return True, ""
