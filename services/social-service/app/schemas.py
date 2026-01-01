from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class LikeBase(BaseModel):
    itinerary_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    comment: str | None = Field(default=None, max_length=500)


class LikeCreate(BaseModel):
    comment: str | None = Field(default=None, max_length=500)


class LikeUpdate(BaseModel):
    comment: str | None = None


class LikeResponse(LikeBase):
    id: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LikeUser(BaseModel):
    id: str
    name: str | None = None
    profile_image_url: str | None = None
    username: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LikeWithUser(LikeResponse):
    user: LikeUser | None = None


class LikeDelete(BaseModel):
    user_id: str


class LikeStatusResponse(BaseModel):
    liked: bool
    total_likes: int
    comment: str | None = None
    like: LikeResponse | None = None


class ItineraryStats(BaseModel):
    total_likes: int
    total_comments: int


class FollowBase(BaseModel):
    follower_id: str = Field(..., min_length=1)
    following_id: str = Field(..., min_length=1)

    @field_validator("following_id")
    @classmethod
    def cannot_follow_self(cls, v: str, info: ValidationInfo) -> str:
        if "follower_id" in info.data and v == info.data["follower_id"]:
            raise ValueError("Cannot follow yourself")
        return v


class FollowCreate(FollowBase):
    pass


class FollowResponse(FollowBase):
    id: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LikesListResponse(BaseModel):
    items: list[LikeWithUser]
    next_cursor: str | None
    has_more: bool


class FollowersListResponse(BaseModel):
    items: list[FollowResponse]
    next_cursor: str | None
    has_more: bool


class FollowingListResponse(BaseModel):
    items: list[FollowResponse]
    next_cursor: str | None
    has_more: bool
