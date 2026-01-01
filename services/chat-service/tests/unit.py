from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.schemas import ConversationCreate
from app.services import ConversationService, MessageService
from core.exceptions import EntityNotFoundException


@pytest.fixture
def mock_centrifugo_client():
    mock = MagicMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
def mock_conversation_service():
    mock = MagicMock(spec=ConversationService)
    return mock


class TestConversationServiceCreate:
    @pytest.mark.asyncio
    async def test_create_conversation_success(self):
        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation.id = "user1_user2"
            mock_conversation.participants = ["user1", "user2"]
            mock_conversation_class.return_value = mock_conversation

            with patch("app.services.verify_participation"):
                service = ConversationService()
                result = await service.create_conversation(["user1", "user2"], "user1")

                assert result is not None

    @pytest.mark.asyncio
    async def test_create_conversation_invalid_participants(self):
        service = ConversationService()

        with pytest.raises(ValueError, match="Conversation must have exactly 2 participants"):
            ConversationCreate(participants=["user1"])

    @pytest.mark.asyncio
    async def test_create_conversation_user_not_participant(self):
        with patch("app.services.verify_participation") as mock_verify:
            from core.exceptions import AuthorizationException

            mock_verify.side_effect = AuthorizationException("User not in participants")

            service = ConversationService()

            with pytest.raises(AuthorizationException):
                await service.create_conversation(["user1", "user2"], "user3")


class TestConversationServiceRead:
    @pytest.mark.asyncio
    async def test_get_conversations_success(self):
        service = ConversationService()

        with patch.object(
            service, "paginate", return_value={"items": [], "next_cursor": None, "has_more": False}
        ):
            result = await service.get_conversations("user1", 20, None)

            assert result is not None
            assert hasattr(result, "conversations")

    @pytest.mark.asyncio
    async def test_get_conversations_without_limit(self):
        service = ConversationService()

        with patch.object(
            service, "paginate", return_value={"items": [], "next_cursor": None, "has_more": False}
        ) as mock_paginate:
            result = await service.get_conversations("user1", None, None)

            mock_paginate.assert_called_once()
            call_kwargs = mock_paginate.call_args[1]
            assert call_kwargs["limit"] == 20
            assert result is not None

    @pytest.mark.asyncio
    async def test_validate_user_participation_success(self):
        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation.participants = ["user1", "user2"]
            mock_conversation_class.collection.get.return_value = mock_conversation

            with patch("app.services.verify_participation"):
                service = ConversationService()
                result = await service.validate_user_participation("conv_id", "user1")

                assert result is True

    @pytest.mark.asyncio
    async def test_validate_user_participation_not_found(self):
        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation_class.collection.get.return_value = None

            service = ConversationService()
            result = await service.validate_user_participation("conv_id", "user1")

            assert result is False


class TestConversationServiceUpdateLastMessageTime:
    @pytest.mark.asyncio
    async def test_update_last_message_time_conversation_exists(self):
        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation_class.collection.get.return_value = mock_conversation

            service = ConversationService()
            test_time = datetime.now()

            await service.update_last_message_time("conv_id", test_time)

            assert mock_conversation.last_message_at == test_time
            mock_conversation.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_last_message_time_conversation_not_found(self):
        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation_class.collection.get.return_value = None

            service = ConversationService()
            test_time = datetime.now()

            await service.update_last_message_time("conv_id", test_time)


class TestMessageServiceCreate:
    @pytest.mark.asyncio
    async def test_add_message_success(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)

        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation.participants = ["user1", "user2"]
            mock_conversation_class.collection.get.return_value = mock_conversation

            with patch("app.services.Message") as mock_message_class:
                mock_message = MagicMock()
                mock_message.id = "msg123"
                mock_message.created_at = datetime.now()
                mock_message_class.return_value = mock_message

                with patch("app.services.verify_participation"):
                    service = MessageService(mock_centrifugo_client, mock_conversation_service)
                    result = await service.add_message("conv_id", "user1", "Hello")

                    assert result is not None

    @pytest.mark.asyncio
    async def test_add_message_conversation_not_found(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)

        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation_class.collection.get.return_value = None

            service = MessageService(mock_centrifugo_client, mock_conversation_service)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.add_message("conv_id", "user1", "Hello")

    @pytest.mark.asyncio
    async def test_add_message_unauthorized(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)

        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation.participants = ["user1", "user2"]
            mock_conversation_class.collection.get.return_value = mock_conversation

            from core.exceptions import AuthorizationException

            with patch(
                "app.services.verify_participation",
                side_effect=AuthorizationException("Not authorized"),
            ):
                service = MessageService(mock_centrifugo_client, mock_conversation_service)

                with pytest.raises(AuthorizationException):
                    await service.add_message("conv_id", "user3", "Hello")


class TestMessageServiceRead:
    @pytest.mark.asyncio
    async def test_get_messages_success(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)

        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation.participants = ["user1", "user2"]
            mock_conversation_class.collection.get.return_value = mock_conversation

            with patch.object(
                MessageService,
                "paginate",
                return_value={"items": [], "next_cursor": None, "has_more": False},
            ):
                with patch("app.services.verify_participation"):
                    service = MessageService(mock_centrifugo_client, mock_conversation_service)
                    result = await service.get_messages("conv_id", "user1", 10, None)

                    assert result is not None
                    assert hasattr(result, "messages")

    @pytest.mark.asyncio
    async def test_get_messages_without_limit(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)

        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation = MagicMock()
            mock_conversation.participants = ["user1", "user2"]
            mock_conversation_class.collection.get.return_value = mock_conversation

            with patch.object(MessageService, "list", return_value=[]):
                with patch("app.services.verify_participation"):
                    service = MessageService(mock_centrifugo_client, mock_conversation_service)
                    result = await service.get_messages("conv_id", "user1", None, None)

                    assert result is not None
                    assert result.next_cursor is None
                    assert result.has_more is False

    @pytest.mark.asyncio
    async def test_get_messages_conversation_not_found(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)

        with patch("app.services.Conversation") as mock_conversation_class:
            mock_conversation_class.collection.get.return_value = None

            service = MessageService(mock_centrifugo_client, mock_conversation_service)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get_messages("conv_id", "user1")


class TestMessageServicePublish:
    @pytest.mark.asyncio
    async def test_publish_message_success(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)
        service = MessageService(mock_centrifugo_client, mock_conversation_service)

        mock_message = MagicMock()
        mock_message.model_dump = Mock(return_value={"id": "msg123", "content": "Hello"})

        await service.publish_message("conv_id", mock_message)

        mock_centrifugo_client.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_message_failure(self, mock_centrifugo_client):
        mock_conversation_service = MagicMock(spec=ConversationService)
        mock_centrifugo_client.publish = AsyncMock(side_effect=Exception("Publish failed"))

        service = MessageService(mock_centrifugo_client, mock_conversation_service)

        mock_message = MagicMock()
        mock_message.model_dump = Mock(return_value={"id": "msg123", "content": "Hello"})

        await service.publish_message("conv_id", mock_message)

        mock_centrifugo_client.publish.assert_called_once()


class TestSchemasValidators:
    def test_conversation_create_validator_valid(self):
        from app.schemas import ConversationCreate

        conversation = ConversationCreate(participants=["user1", "user2"])
        assert conversation.participants == ["user1", "user2"]

    def test_conversation_create_validator_invalid_single(self):
        from app.schemas import ConversationCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate(participants=["user1"])

        assert "Conversation must have exactly 2 participants" in str(exc_info.value)

    def test_conversation_create_validator_invalid_multiple(self):
        from app.schemas import ConversationCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate(participants=["user1", "user2", "user3"])

        assert "Conversation must have exactly 2 participants" in str(exc_info.value)

    def test_send_message_request_validator_valid(self):
        from app.schemas import SendMessageRequest

        message = SendMessageRequest(content="Hello World")
        assert message.content == "Hello World"

    def test_send_message_request_validator_empty_string(self):
        from app.schemas import SendMessageRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SendMessageRequest(content="")

        assert "Content cannot be empty or whitespace only" in str(exc_info.value)

    def test_send_message_request_validator_whitespace_only(self):
        from app.schemas import SendMessageRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SendMessageRequest(content="   ")

        assert "Content cannot be empty or whitespace only" in str(exc_info.value)

    def test_send_message_request_validator_whitespace_with_newlines(self):
        from app.schemas import SendMessageRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SendMessageRequest(content="  \n  \t  ")

        assert "Content cannot be empty or whitespace only" in str(exc_info.value)
