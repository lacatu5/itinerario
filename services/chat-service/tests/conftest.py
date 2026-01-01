import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch


os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")
os.environ.setdefault("ENVIRONMENT", "local")

os.environ.setdefault("CLOUD_STORAGE_BUCKET", "test-bucket")
os.environ.setdefault("CENTRIFUGO_API_URL", "http://localhost")
os.environ.setdefault("CENTRIFUGO_API_KEY", "test-key")
os.environ.setdefault("CENTRIFUGO_WS_URL", "ws://localhost")
os.environ.setdefault("CENTRIFUGO_HMAC_SECRET_KEY", "test-secret-key")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_HOST", "localhost")

from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from datetime import datetime
from app.models import Conversation, Message

from app.main import app


mock_firestore_client = MagicMock()
patch("core.firestore.client.firestore.Client", return_value=mock_firestore_client).start()


async def override_get_current_user_id() -> str:
    return "test_firebase_uid_123"


@pytest.fixture(autouse=True)
def mock_firestore_models():
    mock_collection = MagicMock()

    def mock_filter_method(*args, **kwargs):
        mock_collection.filtered = True
        return mock_collection

    def mock_order_method(*args, **kwargs):
        mock_collection.ordered = True
        return mock_collection

    def mock_fetch_method(*args, **kwargs):
        return []

    def mock_get_method(doc_id):
        return None

    def mock_save(self):
        if not hasattr(self, "id") or not self.id:
            self.id = f"mock_{id(self)}"
        if not hasattr(self, "created_at") or not self.created_at:
            self.created_at = datetime.now()
        if not hasattr(self, "updated_at") or not self.updated_at:
            self.updated_at = datetime.now()

    originals = {}
    for model in [Conversation, Message]:
        originals[model] = {
            "get": model.collection.get,
            "filter": model.collection.filter,
            "fetch": model.collection.fetch,
            "order": model.collection.order,
        }

        model.collection.get = mock_get_method
        model.collection.filter = mock_filter_method
        model.collection.order = mock_order_method
        model.collection.fetch = mock_fetch_method

    with patch.object(Conversation, "save", mock_save), patch.object(Message, "save", mock_save):
        yield

    for model in [Conversation, Message]:
        model.collection.get = originals[model]["get"]
        model.collection.filter = originals[model]["filter"]
        model.collection.fetch = originals[model]["fetch"]
        model.collection.order = originals[model]["order"]


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    from core.auth.firebase import get_current_user_id
    from app.router import get_centrifugo_client

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    mock_centrifugo = MagicMock()

    app.dependency_overrides[get_centrifugo_client] = lambda: mock_centrifugo

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_conversation_data() -> dict:
    return {
        "id": "user1_user2",
        "participants": ["user1", "user2"],
        "last_message_at": None,
    }


@pytest.fixture
def sample_message_data() -> dict:
    return {
        "id": "msg123",
        "conversation_id": "user1_user2",
        "sender_id": "user1",
        "content": "Hello!",
    }


@pytest.fixture
def mock_centrifugo_client() -> MagicMock:
    mock = MagicMock()
    mock.publish = AsyncMock()
    return mock
