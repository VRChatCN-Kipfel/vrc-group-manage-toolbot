"""
VRChat API 客户端
提供与 VRChat API 交互的核心功能
这是一个工具类，供插件调用使用
"""

import asyncio
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx
from nonebot import logger

from .vrc_config import VRCConfig
from .vrc_models import User, Instance, Group, World


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
            
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        
        return self.client
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None
            self._authenticated = False
    
    async def login(self, username: Optional[str] = None, password: Optional[str] = None, 
                   two_factor_code: Optional[str] = None) -> bool:
        """
        登录 VRChat API
        
        Args:
            username: 用户名
            password: 密码
            two_factor_code: 两步验证码
            
        Returns:
            bool: 是否登录成功
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
            response = await client.post(
                "/auth/user",
                data={"username": user, "password": pwd},
            )
            
            if response.status_code == 200:
                # 检查是否需要两步验证
                response_data = response.json()
                
                if response_data.get("requiresTwoFactorAuth"):
                    if not two_factor_code and not self.config.two_factor_code:
                        logger.warning("需要两步验证码")
                        return False
                    
                    # 发送两步验证
                    tfa_code = two_factor_code or self.config.two_factor_code
                    tfa_response = await client.post(
                        "/auth/twofactorauth/totp/verify",
                        json={"code": tfa_code},
                    )
                    
                    if tfa_response.status_code == 200:
                        # 获取认证 cookie
                        auth_cookie = tfa_response.cookies.get("auth")
                        if auth_cookie:
                            self.config.auth_cookie = auth_cookie
                            self._authenticated = True
                            logger.success("VRChat API 登录成功（含两步验证）")
                            return True
                else:
                    # 不需要两步验证
                    auth_cookie = response.cookies.get("auth")
                    if auth_cookie:
                        self.config.auth_cookie = auth_cookie
                        self._authenticated = True
                        logger.success("VRChat API 登录成功")
                        return True
            
            logger.error(f"VRChat API 登录失败: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"VRChat API 登录异常: {e}")
            return False
    
    async def get_current_user(self) -> Optional[User]:
        """
        获取当前用户信息
        
        Returns:
            User: 用户信息，失败返回 None
        """
        try:
            client = await self._get_client()
            response = await client.get("/auth/user")
            
            if response.status_code == 200:
                return User(**response.json())
            else:
                logger.error(f"获取用户信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None
    
    async def get_instance(self, instance_id: str) -> Optional[Instance]:
        """
        获取实例信息
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            Instance: 实例信息，失败返回 None
        """
        try:
            client = await self._get_client()
            response = await client.get(f"/instances/{instance_id}")
            
            if response.status_code == 200:
                return Instance(**response.json())
            else:
                logger.error(f"获取实例信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取实例信息异常: {e}")
            return None
    
    async def get_group(self, group_id: str) -> Optional[Group]:
        """
        获取群组信息
        
        Args:
            group_id: 群组 ID
            
        Returns:
            Group: 群组信息，失败返回 None
        """
        try:
            client = await self._get_client()
            response = await client.get(f"/groups/{group_id}")
            
            if response.status_code == 200:
                return Group(**response.json())
            else:
                logger.error(f"获取群组信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取群组信息异常: {e}")
            return None
    
    async def get_group_instances(self, group_id: str) -> List[Instance]:
        """
        获取群组的实例列表
        
        Args:
            group_id: 群组 ID
            
        Returns:
            List[Instance]: 实例列表
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"/groups/{group_id}/instances",
                params={"offset": 0, "n": 50}
            )
            
            if response.status_code == 200:
                instances_data = response.json()
                return [Instance(**data) for data in instances_data]
            else:
                logger.error(f"获取群组实例失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取群组实例异常: {e}")
            return []
    
    async def get_world(self, world_id: str) -> Optional[World]:
        """
        获取世界信息
        
        Args:
            world_id: 世界 ID
            
        Returns:
            World: 世界信息，失败返回 None
        """
        try:
            client = await self._get_client()
            response = await client.get(f"/worlds/{world_id}")
            
            if response.status_code == 200:
                return World(**response.json())
            else:
                logger.error(f"获取世界信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取世界信息异常: {e}")
            return None
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        获取用户信息
        
        Args:
            user_id: 用户 ID
            
        Returns:
            User: 用户信息，失败返回 None
        """
        try:
            client = await self._get_client()
            response = await client.get(f"/users/{user_id}")
            
            if response.status_code == 200:
                return User(**response.json())
            else:
                logger.error(f"获取用户信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None
    
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
    
    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self._authenticated
