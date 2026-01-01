from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient


class TestGetConversationsEndpoint:
    @pytest.mark.asyncio
    async def test_get_conversations_success(self, client: AsyncClient):
        with patch("app.services.ConversationService.get_conversations") as mock_get:
            mock_get.return_value = {"conversations": [], "next_cursor": None, "has_more": False}

            response = await client.get("/api/chat/conversations")

            assert response.status_code == 200
            data = response.json()
            assert "conversations" in data

    @pytest.mark.asyncio
    async def test_get_conversations_with_limit(self, client: AsyncClient):
        with patch("app.services.ConversationService.get_conversations") as mock_get:
            mock_get.return_value = {
                "conversations": [],
                "next_cursor": "cursor123",
                "has_more": True,
            }

            response = await client.get("/api/chat/conversations?limit=10")

            assert response.status_code == 200
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversations_with_cursor(self, client: AsyncClient):
        with patch("app.services.ConversationService.get_conversations") as mock_get:
            mock_get.return_value = {"conversations": [], "next_cursor": None, "has_more": False}

            response = await client.get("/api/chat/conversations?cursor=test_cursor")

            assert response.status_code == 200


class TestCreateConversationEndpoint:
    @pytest.mark.asyncio
    async def test_create_conversation_success(self, client: AsyncClient):
        with patch("app.services.ConversationService.create_conversation") as mock_create:
            mock_create.return_value = {
                "id": "user1_user2",
                "participants": ["user1", "user2"],
                "last_message_at": None,
            }

            response = await client.post(
                "/api/chat/conversations", json={"participants": ["user1", "user2"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["participants"] == ["user1", "user2"]

    @pytest.mark.asyncio
    async def test_create_conversation_invalid_participants_single(self, client: AsyncClient):
        response = await client.post("/api/chat/conversations", json={"participants": ["user1"]})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_conversation_invalid_participants_three(self, client: AsyncClient):
        response = await client.post(
            "/api/chat/conversations", json={"participants": ["user1", "user2", "user3"]}
        )

        assert response.status_code == 422


class TestGetMessagesEndpoint:
    @pytest.mark.asyncio
    async def test_get_messages_success(self, client: AsyncClient):
        with patch("app.services.MessageService.get_messages") as mock_get:
            mock_get.return_value = {"messages": [], "next_cursor": None, "has_more": False}

            response = await client.get("/api/chat/conversations/conv_id/messages")

            assert response.status_code == 200
            data = response.json()
            assert "messages" in data

    @pytest.mark.asyncio
    async def test_get_messages_with_limit(self, client: AsyncClient):
        with patch("app.services.MessageService.get_messages") as mock_get:
            mock_get.return_value = {"messages": [], "next_cursor": "next_cursor", "has_more": True}

            response = await client.get("/api/chat/conversations/conv_id/messages?limit=50")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_messages_with_cursor(self, client: AsyncClient):
        with patch("app.services.MessageService.get_messages") as mock_get:
            mock_get.return_value = {"messages": [], "next_cursor": None, "has_more": False}

            response = await client.get(
                "/api/chat/conversations/conv_id/messages?cursor=test_cursor"
            )

            assert response.status_code == 200


class TestSendMessageEndpoint:
    @pytest.mark.asyncio
    async def test_send_message_success(self, client: AsyncClient):
        with patch("app.services.MessageService.add_message") as mock_add:
            with patch("app.services.MessageService.publish_message"):
                mock_message = MagicMock()
                mock_message.id = "msg123"
                mock_message.conversation_id = "conv_id"
                mock_message.sender_id = "test_firebase_uid_123"
                mock_message.content = "Hello World"
                mock_message.created_at = "2024-01-01T00:00:00Z"
                mock_add.return_value = mock_message

                response = await client.post(
                    "/api/chat/conversations/conv_id/messages", json={"content": "Hello World"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "msg123"
                assert "created_at" in data

    @pytest.mark.asyncio
    async def test_send_message_empty_content(self, client: AsyncClient):
        response = await client.post(
            "/api/chat/conversations/conv_id/messages", json={"content": ""}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_whitespace_only(self, client: AsyncClient):
        response = await client.post(
            "/api/chat/conversations/conv_id/messages", json={"content": "   "}
        )

        assert response.status_code == 422


class TestCentrifugoTokenEndpoint:
    @pytest.mark.asyncio
    async def test_get_centrifugo_token_success(self, client: AsyncClient):
        with patch("app.router.generate_centrifugo_token", return_value="test_token"):
            response = await client.post("/api/chat/centrifugo-token")

            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert "ws_url" in data
            assert "user_id" in data

    @pytest.mark.asyncio
    async def test_get_centrifugo_token_generation_failure(self, client: AsyncClient):
        with patch(
            "app.router.generate_centrifugo_token", side_effect=Exception("Generation failed")
        ):
            response = await client.post("/api/chat/centrifugo-token")

            assert response.status_code == 403
            assert "Failed to generate Centrifugo token" in response.json()["detail"]
