"""
VRChat API 数据模型
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    """用户模型"""
    id: str
    displayName: str
    username: Optional[str] = None
    status: Optional[str] = None
    state: Optional[str] = None
    avatarThumbnail: Optional[str] = None
    currentAvatar: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        extra = "allow"  # 允许额外字段


class Instance(BaseModel):
    """实例模型"""
    id: str
    name: Optional[str] = None
    worldId: Optional[str] = None
    worldName: Optional[str] = None
    region: Optional[str] = None
    groupId: Optional[str] = None
    groupAccessType: Optional[str] = None  # public, plus, members
    capacity: Optional[int] = None
    userCount: Optional[int] = None
    n_users: Optional[List[dict]] = []
    instanceCreatorDisplayName: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @property
    def full_instance_id(self) -> str:
        """获取完整的实例 ID"""
        return self.id
    
    class Config:
        extra = "allow"


class Group(BaseModel):
    """群组模型"""
    id: str
    name: str
    shortCode: Optional[str] = None
    discriminator: Optional[str] = None
    description: Optional[str] = None
    iconUrl: Optional[str] = None
    bannerUrl: Optional[str] = None
    privacy: Optional[str] = None  # public, plus, members, private
    memberCount: Optional[int] = None
    onlineMemberCount: Optional[int] = None
    
    class Config:
        extra = "allow"


class World(BaseModel):
    """世界模型"""
    id: str
    name: str
    authorName: Optional[str] = None
    authorId: Optional[str] = None
    capacity: Optional[int] = None
    recommendedCapacity: Optional[int] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    thumbnailImageUrl: Optional[str] = None
    tags: Optional[List[str]] = []
    
    class Config:
        extra = "allow"
