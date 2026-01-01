from fastapi import APIRouter, Depends, Query, Request

from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationsResponse,
    MessagesResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services import ConversationService, MessageService
from core.auth.firebase import get_current_user_id
from core.config import centrifugo_settings
from core.exceptions import AuthorizationException
from core.messaging.client import CentrifugoClient
from core.messaging.utils import generate_centrifugo_token


def get_conversation_service() -> ConversationService:
    return ConversationService()


def get_centrifugo_client(request: Request) -> CentrifugoClient:
    return request.app.state.centrifugo_client


def get_message_service(
    centrifugo_client: CentrifugoClient = Depends(get_centrifugo_client),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> MessageService:
    return MessageService(centrifugo_client, conversation_service)


api_router = APIRouter(prefix="/api/chat", tags=["Chat"])


@api_router.get(
    "/conversations", response_model=ConversationsResponse, summary="List user conversations"
)
async def get_conversations(
    limit: int | None = Query(None, ge=1, le=100),
    cursor: str | None = Query(None),
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    return await conversation_service.get_conversations(user_id, limit, cursor)


@api_router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessagesResponse,
    summary="Get conversation messages",
)
async def get_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=100),
    cursor: str | None = Query(None),
    user_id: str = Depends(get_current_user_id),
    message_service: MessageService = Depends(get_message_service),
):
    return await message_service.get_messages(conversation_id, user_id, limit, cursor)


@api_router.post(
    "/conversations", response_model=ConversationResponse, summary="Create new conversation"
)
async def create_conversation(
    payload: ConversationCreate,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    return await conversation_service.create_conversation(payload.participants, user_id)


@api_router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    summary="Send message to conversation",
)
async def send_message(
    conversation_id: str,
    payload: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    message_service: MessageService = Depends(get_message_service),
):
    message = await message_service.add_message(
        conversation_id, sender_id=user_id, content=payload.content
    )
    await message_service.publish_message(conversation_id, message)
    return message


@api_router.post("/centrifugo-token", summary="Get Centrifugo WebSocket token")
async def get_centrifugo_token(
    user_id: str = Depends(get_current_user_id),
):
    try:
        token = generate_centrifugo_token(user_id, centrifugo_settings.CENTRIFUGO_HMAC_SECRET_KEY)
        return {
            "token": token,
            "ws_url": centrifugo_settings.CENTRIFUGO_WS_URL,
            "user_id": user_id,
        }
    except Exception:
        raise AuthorizationException("Failed to generate Centrifugo token")
