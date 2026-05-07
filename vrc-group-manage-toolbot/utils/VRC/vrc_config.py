"""
VRChat API 配置模块
"""

from typing import Optional
from pydantic import BaseModel


class VRCConfig(BaseModel):
    """VRChat API 配置"""
    
    # API 基础 URL
    base_url: str = "https://api.vrchat.cloud/api/1"
    
    # 认证信息
    username: Optional[str] = None
    password: Optional[str] = None
    two_factor_code: Optional[str] = None
    
    # Cookie 存储（登录后获取）
    auth_cookie: Optional[str] = None
    
    # 请求超时设置（秒）
    timeout: int = 30
    
    # 请求间隔（避免速率限制，毫秒）
    request_delay: int = 1000
    
    class Config:
        env_prefix = "VRC_"
        
    @classmethod
    def from_env(cls) -> "VRCConfig":
        from nonebot import get_driver
        cfg = get_driver().config
        return cls(
            username=getattr(cfg, "vrc_username", None),
            password=getattr(cfg, "vrc_password", None),
            auth_cookie=getattr(cfg, "vrc_auth_cookie", None),
            timeout=int(getattr(cfg, "vrc_timeout", 30)),
            request_delay=int(getattr(cfg, "vrc_request_delay", 1000)),
        )
