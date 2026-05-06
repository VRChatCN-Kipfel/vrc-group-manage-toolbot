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
        """从环境变量加载配置"""
        import os
        return cls(
            username=os.getenv("VRC_USERNAME"),
            password=os.getenv("VRC_PASSWORD"),
            auth_cookie=os.getenv("VRC_AUTH_COOKIE"),
            timeout=int(os.getenv("VRC_TIMEOUT", "30")),
            request_delay=int(os.getenv("VRC_REQUEST_DELAY", "1000")),
        )
