"""
VRChat API 数据模型
"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class User(BaseModel):
    """用户模型"""
    id: str
    displayName: str
    username: Optional[str] = None
    status: Optional[str] = None
    state: Optional[str] = None
    bio: Optional[str] = None
    bioLinks: Optional[List[str]] = None
    avatarThumbnail: Optional[str] = None
    currentAvatar: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        extra = "allow"  # 允许额外字段


class Instance(BaseModel):
    """实例模型"""
    id: str = Field(alias="instanceId")
    worldId: str = Field(default="", alias="world")
    worldName: Optional[str] = None
    region: Optional[str] = None
    location: Optional[str] = None
    userCount: int = Field(default=0, alias="memberCount")
    capacity: Optional[int] = None
    groupId: Optional[str] = None
    groupAccessType: Optional[str] = None
    name: Optional[str] = None
    n_users: Optional[List[dict]] = None
    instanceCreatorDisplayName: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @field_validator("n_users", mode="before")
    def normalize_n_users(cls, v):
        if isinstance(v, int):
            return None
        return v
    
    @property
    def full_instance_id(self) -> str:
        return self.id
    
    @property
    def display_count(self) -> str:
        cap = self.capacity or "?"
        return f"{self.userCount}/{cap}"
    
    @field_validator("worldId", mode="before")
    def extract_world_id(cls, v):
        if isinstance(v, dict):
            return v.get("id", v.get("worldId", ""))
        return v or ""
    
    @model_validator(mode="before")
    def normalize_world_dict(cls, values):
        world = values.get("world")
        if isinstance(world, dict):
            values["world"] = world.get("id", "")
            if not values.get("worldName") and world.get("name"):
                values["worldName"] = world["name"]
            if not values.get("capacity") and world.get("capacity"):
                values["capacity"] = world["capacity"]
        return values
    
    @field_validator("location", mode="before")
    def extract_location(cls, v):
        if isinstance(v, dict):
            return v.get("location", v.get("instanceId", str(v)))
        return v
    
    class Config:
        extra = "allow"
        populate_by_name = True


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


class GroupMember(BaseModel):
    id: str
    groupId: str
    userId: str
    roleIds: List[str] = []
    isRepresenting: bool = False
    joinedAt: Optional[str] = None

    class Config:
        extra = "allow"


class GroupRole(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    selfAssignable: bool = False
    isManagement: bool = False
    permissions: List[str] = []

    class Config:
        extra = "allow"


class Announcement(BaseModel):
    id: str
    title: str
    text: str
    createdAt: Optional[str] = None

    class Config:
        extra = "allow"


class JoinRequest(BaseModel):
    userId: str
    created_at: Optional[str] = None

    class Config:
        extra = "allow"


class AuditLogEntry(BaseModel):
    id: str
    created_at: Optional[str] = None
    description: Optional[str] = None
    actorId: Optional[str] = None
    targetId: Optional[str] = None

    class Config:
        extra = "allow"
