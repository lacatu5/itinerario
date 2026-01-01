import asyncio
import os

os.environ.setdefault("CLOUD_STORAGE_BUCKET", "test-bucket")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("CENTRIFUGO_API_URL", "http://localhost")
os.environ.setdefault("CENTRIFUGO_API_KEY", "test-key")
os.environ.setdefault("CENTRIFUGO_HMAC_SECRET_KEY", "test-secret-key")
os.environ.setdefault("CENTRIFUGO_WS_URL", "ws://localhost")

from datetime import date, datetime
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models import Base, Itinerary
from core.database.connection import get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
def mock_user_resolver():
    with patch("app.services.UserResolver") as mock_resolver_class:
        resolver_instance = AsyncMock()
        resolver_instance.get_user_id.return_value = 123
        mock_resolver_class.return_value = resolver_instance
        yield resolver_instance


engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


async def override_get_current_user_id() -> str:
    return "test_firebase_uid_123"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        trans = await session.begin()
        try:
            yield session
        finally:
            await trans.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db

    from core.auth.firebase import get_current_user_id

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_itinerary_data() -> dict:
    return {
        "title": "Test Trip to Paris",
        "destination": "Paris",
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 6, 10),
        "short_description": "Amazing trip",
        "detail_description": "Detailed description of the trip",
        "image_url": None,
        "latitude": None,
        "longitude": None,
        "address": None,
    }


@pytest.fixture
def sample_location_data() -> dict:
    return {
        "name": "Eiffel Tower",
        "short_description": "Famous landmark",
        "from_date": date(2024, 6, 1),
        "to_date": date(2024, 6, 1),
        "image_url": None,
        "latitude": None,
        "longitude": None,
        "address": None,
    }


@pytest.fixture
def sample_transport_data() -> dict:
    return {
        "type": "flight",
        "departure_location": "JFK",
        "arrival_location": "CDG",
        "departure_time": datetime(2024, 6, 1, 10, 0),
        "arrival_time": datetime(2024, 6, 1, 22, 0),
        "carrier": "Air France",
        "transport_number": "AF123",
    }


@pytest.fixture
def sample_itinerary(sample_itinerary_data: dict) -> Itinerary:
    return Itinerary(id=1, owner_id="test_firebase_uid_123", **sample_itinerary_data)


@pytest.fixture
def mock_upload_file() -> MagicMock:
    mock = MagicMock()
    mock.filename = "test.jpg"
    mock.content_type = "image/jpeg"
    mock.file = MagicMock()
    return mock
