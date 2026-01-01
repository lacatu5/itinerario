import asyncio
import os
from unittest.mock import MagicMock, patch

os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")
os.environ.setdefault("ENVIRONMENT", "local")

os.environ.setdefault("CLOUD_STORAGE_BUCKET", "test-bucket")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("CENTRIFUGO_API_URL", "http://localhost:8000")
os.environ.setdefault("CENTRIFUGO_API_KEY", "test-api-key")
os.environ.setdefault("CENTRIFUGO_WS_URL", "ws://localhost:8000")
os.environ.setdefault("CENTRIFUGO_HMAC_SECRET_KEY", "test-hmac-secret-key")

from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from datetime import datetime

from app.models import Advertisement, Destination, Discount, Offer

# Mock Firestore client at the module level before app imports
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
    for model in [Destination, Offer, Discount, Advertisement]:
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

    with (
        patch.object(Destination, "save", mock_save),
        patch.object(Offer, "save", mock_save),
        patch.object(Discount, "save", mock_save),
        patch.object(Advertisement, "save", mock_save),
    ):
        yield

    for model in [Destination, Offer, Discount, Advertisement]:
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

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_destination_data() -> dict:
    return {
        "id": "dest123",
        "owner_id": "user123",
        "name": "Paris",
        "region": "Île-de-France",
        "country": "France",
        "description": "Beautiful city",
        "image_url": None,
        "latitude": "48.8566",
        "longitude": "2.3522",
        "address": None,
    }


@pytest.fixture
def sample_offer_data() -> dict:
    return {
        "id": "offer123",
        "destination_id": "dest123",
        "title": "Special Offer",
        "description": "Great deal",
        "accommodation_name": "Hotel Paris",
        "price": 100.0,
        "discount_percentage": 20,
        "valid_from": None,
        "valid_until": None,
        "image_url": None,
        "link_url": None,
        "active": True,
    }


@pytest.fixture
def sample_discount_data() -> dict:
    return {
        "id": "discount123",
        "destination_id": "dest123",
        "title": "Museum Discount",
        "description": "50% off",
        "attraction_name": "Louvre",
        "discount_percentage": 50,
        "valid_from": None,
        "valid_until": None,
        "promo_code": "LOUVRE50",
        "link_url": None,
        "active": True,
    }


@pytest.fixture
def sample_advertisement_data() -> dict:
    return {
        "id": "ad123",
        "destination_id": "dest123",
        "title": "Paris Event",
        "description": "Annual festival",
        "event_date": None,
        "image_url": None,
        "link_url": None,
        "active": True,
    }


@pytest.fixture
def mock_upload_file() -> MagicMock:
    mock = MagicMock()
    mock.filename = "test.jpg"
    mock.content_type = "image/jpeg"
    mock.file = MagicMock()
    return mock
