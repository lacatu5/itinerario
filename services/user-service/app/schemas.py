from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    username: str | None = Field(default=None, min_length=3, max_length=50)
    profile_image_url: str | None = None


class UserCreate(UserBase):
    firebase_uid: str


class UserUpdate(BaseModel):
    name: str | None = None
    username: str | None = None
    profile_image_url: str | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firebase_uid: str
    created_at: datetime
    updated_at: datetime | None = None


class PublicUserResponse(BaseModel):
    id: int
    firebase_uid: str
    name: str
    username: str | None = None
    profile_image_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchUsersResponse(BaseModel):
    users: list[UserResponse]
    total_count: int
