from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConversationBase(BaseModel):
    participants: list[str] = Field(..., description="List of exactly 2 participant user IDs")

    @field_validator("participants")
    @classmethod
    def validate_participants(cls, v):
        if len(v) != 2:
            raise ValueError("Conversation must have exactly 2 participants")
        return v


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    participants: list[str] | None = Field(default=None, min_length=2, max_length=2)


class ConversationResponse(ConversationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str = ""
    created_at: datetime | None = None
    last_message_at: datetime | None = None


class ConversationsResponse(BaseModel):
    conversations: list[ConversationResponse]
    next_cursor: str | None
    has_more: bool


class MessageBase(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    sender_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1, max_length=5000)


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=5000)


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SendMessageRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v


class SendMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class MessagesResponse(BaseModel):
    messages: list[MessageResponse]
    next_cursor: str | None
    has_more: bool
