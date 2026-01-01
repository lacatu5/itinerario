from loguru import logger

from app.models import Conversation, Message
from app.schemas import (
    ConversationResponse,
    ConversationsResponse,
    MessageResponse,
    MessagesResponse,
)
from core.auth.ownership import verify_participation
from core.exceptions import EntityNotFoundException
from core.firestore.models import BaseFirestoreService
from core.messaging.client import CentrifugoClient


class ConversationService(BaseFirestoreService):
    def __init__(self):
        super().__init__(Conversation, ConversationResponse)

    async def get_conversations(
        self, user_id: str, limit: int | None = None, cursor: str | None = None
    ) -> ConversationsResponse:
        if not limit:
            limit = 20

        result = self.paginate(
            filters={"participants": {"op": "array_contains", "value": user_id}},
            order_by="last_message_at",
            limit=limit,
            cursor=cursor,
        )

        logger.info(f"Retrieved {len(result['items'])} conversations for user {user_id}")
        return ConversationsResponse(
            conversations=result["items"],
            next_cursor=result["next_cursor"],
            has_more=result["has_more"],
        )

    async def create_conversation(
        self, participants: list[str], user_id: str
    ) -> ConversationResponse:
        verify_participation(participants, user_id, "conversation")

        conversation_key = ":".join(sorted(participants))
        conversation = Conversation()
        conversation.id = conversation_key
        conversation.participants = participants
        conversation.last_message_at = None
        conversation.save()

        logger.info(f"Created conversation with {len(participants)} participants")
        return ConversationResponse.model_validate(conversation)

    async def validate_user_participation(self, conversation_id: str, user_id: str) -> bool:
        conversation = Conversation.collection.get(conversation_id)
        if not conversation:
            return False
        verify_participation(conversation.participants, user_id, "conversation")
        logger.debug(f"User {user_id} participation validated for conversation {conversation_id}")
        return True

    async def update_last_message_time(self, conversation_id: str, message_created_at):
        conversation = Conversation.collection.get(conversation_id)
        if conversation:
            conversation.last_message_at = message_created_at
            conversation.save()


class MessageService(BaseFirestoreService):
    def __init__(
        self,
        centrifugo_client: CentrifugoClient,
        conversation_service: ConversationService,
    ):
        super().__init__(Message, MessageResponse)
        self.centrifugo = centrifugo_client
        self.conversations = conversation_service

    async def add_message(
        self, conversation_id: str, sender_id: str, content: str
    ) -> MessageResponse:
        conversation = Conversation.collection.get(conversation_id)
        if not conversation:
            raise EntityNotFoundException(f"Conversation {conversation_id} not found")
        verify_participation(conversation.participants, sender_id, "conversation")

        message = Message()
        message.conversation_id = conversation_id
        message.sender_id = sender_id
        message.content = content
        message.save()

        await self.conversations.update_last_message_time(conversation_id, message.created_at)

        logger.info(f"Message added to conversation {conversation_id} by user {sender_id}")

        return MessageResponse.model_validate(message)

    async def publish_message(self, conversation_id: str, message: MessageResponse):
        try:
            await self.centrifugo.publish(
                f"chat:{conversation_id}", message.model_dump(mode="json")
            )
            logger.info(f"Message published to conversation {conversation_id}")
        except Exception as e:
            logger.opt(exception=True).error(
                f"Failed to publish message to conversation {conversation_id}: {e}"
            )

    async def get_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> MessagesResponse:
        conversation = Conversation.collection.get(conversation_id)
        if not conversation:
            raise EntityNotFoundException(f"Conversation {conversation_id} not found")
        verify_participation(conversation.participants, user_id, "conversation")

        if limit:
            result = self.paginate(
                filters={"conversation_id": conversation_id},
                order_by="-created_at",
                limit=limit,
                cursor=cursor,
            )
            messages = result["items"][::-1]
            next_cursor = result["next_cursor"]
            has_more = result["has_more"]
        else:
            messages = self.list(
                filters={"conversation_id": conversation_id},
                order_by="created_at",
            )
            next_cursor = None
            has_more = False

        logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
        return MessagesResponse(messages=messages, next_cursor=next_cursor, has_more=has_more)
