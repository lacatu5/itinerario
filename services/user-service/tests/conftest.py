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
os.environ.setdefault("CENTRIFUGO_WS_URL", "ws://localhost")
os.environ.setdefault("CENTRIFUGO_HMAC_SECRET_KEY", "test-secret-key")

from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models import Base, User
from core.database.connection import get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

_db_session_context: AsyncSession | None = None


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    global _db_session_context
    if _db_session_context is not None:
        yield _db_session_context
    else:
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
    global _db_session_context
    async with TestingSessionLocal() as session:
        _db_session_context = session
        try:
            yield session
        finally:
            _db_session_context = None
            await session.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database():
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db

    from core.auth.firebase import get_current_user_id

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict:
    return {
        "firebase_uid": "test_firebase_uid_123",
        "email": "test@example.com",
        "name": "Test User",
        "username": "testuser",
    }


@pytest.fixture
def auth_user_id() -> str:
    return "test_firebase_uid_123"


@pytest.fixture
def sample_user(sample_user_data: dict) -> User:
    return User(id=1, **sample_user_data)


@pytest.fixture
def mock_firebase_user() -> MagicMock:
    mock = MagicMock()
    mock.user_id = "test_firebase_uid_123"
    mock.email = "test@example.com"
    mock.name = "Test User"
    return mock


@pytest.fixture
def mock_upload_file() -> MagicMock:
    mock = MagicMock()
    mock.filename = "test.jpg"
    mock.content_type = "image/jpeg"
    mock.file = MagicMock()
    return mock


@pytest.fixture
def multiple_users_data() -> list[dict]:
    return [
        {
            "firebase_uid": "user1_uid",
            "email": "user1@example.com",
            "name": "User One",
            "username": "userone",
        },
        {
            "firebase_uid": "user2_uid",
            "email": "user2@example.com",
            "name": "User Two",
            "username": "usertwo",
        },
        {
            "firebase_uid": "user3_uid",
            "email": "user3@example.com",
            "name": "User Three",
            "username": "userthree",
        },
    ]
