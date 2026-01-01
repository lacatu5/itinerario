import asyncio
import os
from unittest.mock import MagicMock, patch

os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")
os.environ.setdefault("ENVIRONMENT", "local")

os.environ.setdefault("CLOUD_STORAGE_BUCKET", "test-bucket")
os.environ.setdefault("OPEN_METEO_AVAILABLE", "false")
os.environ.setdefault("ENABLE_MOCK_DATA", "true")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("CENTRIFUGO_API_URL", "http://localhost:8000")
os.environ.setdefault("CENTRIFUGO_API_KEY", "test-api-key")
os.environ.setdefault("CENTRIFUGO_HMAC_SECRET_KEY", "test-secret-key")
os.environ.setdefault("CENTRIFUGO_WS_URL", "ws://localhost:8000")

from datetime import datetime
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


mock_firestore_client = MagicMock()
patch("core.firestore.client.firestore.Client", return_value=mock_firestore_client).start()


async def override_get_current_user_id() -> str:
    return "test_firebase_uid_123"


@pytest.fixture(autouse=True)
def mock_firestore_models():
    from app.models import TravelWarning, TrackedFlight, UserFlightTracking

    original_get = TravelWarning.collection.get
    original_filter = TravelWarning.collection.filter
    original_fetch = TravelWarning.collection.fetch
    original_order = TravelWarning.collection.order

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

    TravelWarning.collection.get = mock_get_method
    TravelWarning.collection.filter = mock_filter_method
    TravelWarning.collection.order = mock_order_method
    TravelWarning.collection.fetch = mock_fetch_method

    TrackedFlight.collection.get = mock_get_method
    TrackedFlight.collection.filter = mock_filter_method
    TrackedFlight.collection.order = mock_order_method
    TrackedFlight.collection.fetch = mock_fetch_method

    UserFlightTracking.collection.get = mock_get_method
    UserFlightTracking.collection.filter = mock_filter_method
    UserFlightTracking.collection.fetch = mock_fetch_method

    def mock_save(self):
        if not hasattr(self, "id") or not self.id:
            self.id = f"mock_{id(self)}"
        if not hasattr(self, "created_at") or not self.created_at:
            self.created_at = datetime.now()
        if not hasattr(self, "updated_at") or not self.updated_at:
            self.updated_at = datetime.now()

    with (
        patch.object(TravelWarning, "save", mock_save),
        patch.object(TrackedFlight, "save", mock_save),
        patch.object(UserFlightTracking, "save", mock_save),
    ):
        yield

    TravelWarning.collection.get = original_get
    TravelWarning.collection.filter = original_filter
    TravelWarning.collection.fetch = original_fetch
    TravelWarning.collection.order = original_order


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
def sample_travel_warning_data() -> dict:
    return {
        "id": "warning123",
        "country_code": "FR",
        "country_name": "France",
        "region": "Paris",
        "severity": "medium",
        "title": "Strike Alert",
        "description": "Transportation strikes expected",
        "category": "transport",
        "source": "Local Authority",
        "source_url": "https://example.com",
        "valid_from": datetime.now(),
        "valid_until": None,
        "active": True,
    }


@pytest.fixture
def sample_tracked_flight_data() -> dict:
    return {
        "id": "flight123",
        "flight_number": "AF123",
        "airline": "Air France",
        "departure_airport": "CDG",
        "arrival_airport": "JFK",
        "scheduled_departure": datetime(2024, 6, 1, 10, 0),
        "scheduled_arrival": datetime(2024, 6, 1, 16, 0),
        "actual_departure": None,
        "actual_arrival": None,
        "status": "scheduled",
        "delay_minutes": None,
        "gate": None,
        "terminal": None,
        "alert_type": None,
        "alert_message": None,
    }


@pytest.fixture
def sample_user_tracking_data() -> dict:
    return {
        "id": "tracking123",
        "user_id": "user123",
        "tracked_flight_id": "flight123",
        "active": True,
    }
