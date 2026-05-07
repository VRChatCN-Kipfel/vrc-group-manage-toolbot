"""
VRChat API 客户端
提供与 VRChat API 交互的核心功能
这是一个工具类，供插件调用使用
"""

import asyncio
import base64
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx
from nonebot import logger

from .vrc_config import VRCConfig
from .vrc_models import (
    User, Instance, Group, World,
    GroupMember, GroupRole, Announcement, JoinRequest, AuditLogEntry,
)


class VRCClient:
    """VRChat API 客户端 - 工具类"""
    
    def __init__(self, config: Optional[VRCConfig] = None):
        """
        初始化 VRChat API 客户端
        
        Args:
            config: VRChat API 配置，如果为 None 则从环境变量加载
        """
        self.config = config or VRCConfig.from_env()
        self.client: Optional[httpx.AsyncClient] = None
        self._authenticated = False
        
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self.client is None:
            headers = {
                "User-Agent": "VRChat-Group-Manage-ToolBot/1.0",
                "Accept": "application/json",
            }
            
            # 如果有认证 cookie，添加到请求头
            if self.config.auth_cookie:
                headers["Cookie"] = f"auth={self.config.auth_cookie}"
                logger.info(f"Auth cookie set, first 10 chars: {self.config.auth_cookie[:10]}...")
            else:
                logger.debug("No auth cookie set")
            
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        
        return self.client
    
    async def _request(self, method: str, path: str, **kwargs) -> dict:
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None
            self._authenticated = False
    
    async def verify_2fa(self, tfa_code: str):
        try:
            user = self.config.username
            pwd = self.config.password
            if not user or not pwd:
                return False
            client = await self._get_client()
            logger.info(f"Submitting 2FA code: {tfa_code}")
            tfa_response = await client.post(
                "/auth/twofactorauth/totp/verify",
                json={"code": tfa_code},
            )
            logger.info(f"2FA verify status: {tfa_response.status_code}")
            if tfa_response.status_code == 429:
                logger.warning("2FA verify 429 rate limited, waiting 5s and retrying...")
                await asyncio.sleep(5)
                tfa_response = await client.post(
                    "/auth/twofactorauth/totp/verify",
                    json={"code": tfa_code},
                )
                logger.info(f"2FA verify retry status: {tfa_response.status_code}")
            if tfa_response.status_code != 200:
                logger.error(f"2FA verify non-200: {tfa_response.text[:200]}")
                return False
            twofa_cookie = tfa_response.cookies.get("twoFactorAuth")
            if not twofa_cookie:
                logger.error(f"No twoFactorAuth, cookies: {dict(tfa_response.cookies)}")
                return False
            logger.info(f"2FA verify passed, getting final auth cookie...")
            auth_bytes = f"{user}:{pwd}".encode("utf-8")
            auth_b64 = base64.b64encode(auth_bytes).decode()
            final_client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={
                    "User-Agent": "VRChat-Group-Manage-ToolBot/1.0",
                    "Authorization": f"Basic {auth_b64}",
                    "Cookie": f"twoFactorAuth={twofa_cookie}",
                },
                timeout=self.config.timeout,
            )
            try:
                final_response = await final_client.get("/auth/user")
                logger.info(f"Final auth: {final_response.status_code}, "
                           f"cookies={list(dict(final_response.cookies).keys())}")
                if final_response.status_code == 200:
                    final_cookie = final_response.cookies.get("auth")
                    if final_cookie:
                        self.config.auth_cookie = final_cookie
                        self.client = None
                        self._authenticated = True
                        logger.success("VRChat API 登录成功（两步验证）")
                        return True
                    else:
                        logger.error(f"No auth cookie: {dict(final_response.cookies)}")
                else:
                    logger.error(f"Final auth failed: {final_response.status_code}")
            finally:
                await final_client.aclose()
            return False
        except Exception as e:
            logger.error(f"2FA exception: {e}")
            return False

    async def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        登录 VRChat API
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            True: 登录成功
            "need_2fa": 需要两步验证
            False: 登录失败
        """
        try:
            client = await self._get_client()
            
            # 使用提供的凭据或配置中的凭据
            user = username or self.config.username
            pwd = password or self.config.password
            
            if not user or not pwd:
                logger.error("缺少用户名或密码")
                return False
            
            # 发送登录请求
            response = await client.get(
                "/auth/user",
                auth=(user, pwd),
            )
            
            if response.status_code == 200:
                # 检查是否需要两步验证
                response_data = response.json()
                
                if response_data.get("requiresTwoFactorAuth"):
                    logger.info("需要两步验证码，请使用 #2fa <验证码>")
                    return "need_2fa"
                else:
                    # 不需要两步验证
                    auth_cookie = response.cookies.get("auth")
                    if auth_cookie:
                        self.config.auth_cookie = auth_cookie
                        self.client = None
                        self._authenticated = True
                        logger.success("VRChat API 登录成功")
                        return True
            
            logger.error(f"VRChat API 登录失败: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"VRChat API 登录异常: {e}")
            return False
    
    async def get_current_user(self) -> Optional[User]:
        try:
            r = await self._request("GET", "/auth/user")
            return User(**r)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return None
            raise
    
    async def get_instance(self, instance_id: str) -> Optional[Instance]:
        try:
            r = await self._request("GET", f"/instances/{instance_id}")
            return Instance(**r)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    async def get_group(self, group_id: str) -> Optional[Group]:
        try:
            r = await self._request("GET", f"/groups/{group_id}")
            return Group(**r)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    async def get_group_instances(self, group_id: str) -> List[Instance]:
        r = await self._request("GET", f"/groups/{group_id}/instances",
                                params={"offset": 0, "n": 50})
        return [Instance(**data) for data in r]
    
    async def get_world(self, world_id: str) -> Optional[World]:
        try:
            r = await self._request("GET", f"/worlds/{world_id}")
            return World(**r)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        try:
            r = await self._request("GET", f"/users/{user_id}")
            return User(**r)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    async def join_instance(self, instance_id: str) -> bool:
        """
        加入实例（需要认证）
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            bool: 是否成功
        """
        try:
            client = await self._get_client()
            response = await client.put(f"/instances/{instance_id}/join")
            
            if response.status_code == 200:
                logger.success(f"成功加入实例: {instance_id}")
                return True
            else:
                logger.error(f"加入实例失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"加入实例异常: {e}")
            return False
    
    async def leave_instance(self, instance_id: str) -> bool:
        """
        离开实例（需要认证）
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            bool: 是否成功
        """
        try:
            client = await self._get_client()
            response = await client.delete(f"/instances/{instance_id}/leave")
            
            if response.status_code == 200:
                logger.success(f"成功离开实例: {instance_id}")
                return True
            else:
                logger.error(f"离开实例失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"离开实例异常: {e}")
            return False
    
    async def refresh_auth(self) -> bool:
        """
        刷新认证状态
        
        Returns:
            bool: 是否成功
        """
        try:
            client = await self._get_client()
            response = await client.get("/auth/user")
            
            if response.status_code == 200:
                self._authenticated = True
                logger.success("认证状态刷新成功")
                return True
            else:
                self._authenticated = False
                logger.warning("认证状态已过期")
                return False
                
        except Exception as e:
            logger.error(f"刷新认证异常: {e}")
            self._authenticated = False
            return False
    
    async def get_group_members(self, group_id: str, n: int = 100, offset: int = 0) -> List[GroupMember]:
        response = await self._request(
            "GET", f"/groups/{group_id}/members",
            params={"n": n, "offset": offset},
        )
        return [GroupMember(**item) for item in response]

    async def get_group_member(self, group_id: str, user_id: str) -> Optional[GroupMember]:
        try:
            response = await self._request(
                "GET", f"/groups/{group_id}/members/{user_id}",
            )
            return GroupMember(**response)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def invite_user_to_group(self, group_id: str, user_id: str) -> dict:
        return await self._request(
            "POST", f"/groups/{group_id}/invite",
            json={"userId": user_id},
        )

    async def kick_user_from_group(self, group_id: str, user_id: str) -> dict:
        return await self._request(
            "DELETE", f"/groups/{group_id}/members/{user_id}",
        )

    async def ban_user_from_group(self, group_id: str, user_id: str) -> dict:
        return await self._request(
            "POST", f"/groups/{group_id}/bans",
            json={"userId": user_id},
        )

    async def unban_user_from_group(self, group_id: str, user_id: str) -> dict:
        return await self._request(
            "DELETE", f"/groups/{group_id}/bans/{user_id}",
        )

    async def get_group_roles(self, group_id: str) -> List[GroupRole]:
        response = await self._request(
            "GET", f"/groups/{group_id}/roles",
        )
        return [GroupRole(**item) for item in response]

    async def update_member_role(self, group_id: str, user_id: str, role_ids: List[str]) -> dict:
        return await self._request(
            "PUT", f"/groups/{group_id}/members/{user_id}/roles",
            json={"roleIds": role_ids},
        )

    async def get_group_announcements(self, group_id: str) -> List[Announcement]:
        response = await self._request(
            "GET", f"/groups/{group_id}/announcement",
        )
        return [Announcement(**item) for item in response]

    async def create_group_announcement(self, group_id: str, title: str, text: str) -> dict:
        return await self._request(
            "POST", f"/groups/{group_id}/announcement",
            json={"title": title, "text": text},
        )

    async def delete_group_announcement(self, group_id: str, announcement_id: str) -> dict:
        return await self._request(
            "DELETE", f"/groups/{group_id}/announcement/{announcement_id}",
        )

    async def get_group_join_requests(self, group_id: str) -> List[JoinRequest]:
        response = await self._request(
            "GET", f"/groups/{group_id}/requests",
        )
        return [JoinRequest(**item) for item in response]

    async def respond_join_request(self, group_id: str, user_id: str, action: str) -> dict:
        return await self._request(
            "PUT", f"/groups/{group_id}/requests/{user_id}",
            json={"action": action},
        )

    async def get_group_audit_logs(self, group_id: str, n: int = 50) -> List[AuditLogEntry]:
        response = await self._request(
            "GET", f"/groups/{group_id}/auditlog",
            params={"n": n},
        )
        return [AuditLogEntry(**item) for item in response]

    async def get_friends(self) -> list:
        response = await self._request(
            "GET", "/auth/user/friends",
        )
        return response if isinstance(response, list) else []

    async def send_friend_request(self, user_id: str) -> dict:
        return await self._request(
            "POST", f"/user/{user_id}/friendRequest",
        )

    async def check_friend_status(self, user_id: str) -> dict:
        return await self._request(
            "GET", f"/user/{user_id}/friendStatus",
        )

    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self._authenticated
