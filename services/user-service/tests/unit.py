from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.services import UserService, generate_username_from_email
from core.exceptions import EntityNotFoundException, ValidationException


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_user_response():
    return UserResponse(
        id=1,
        firebase_uid="test_firebase_uid_123",
        email="test@example.com",
        name="Test User",
        username="testuser",
        profile_image_url=None,
        created_at=datetime.now(),
        updated_at=None,
    )


class TestUserServiceCreate:
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db_session, sample_user_response):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        user_data = UserCreate(
            firebase_uid="test_uid", email="new@example.com", name="Test", username="test123"
        )

        with patch.object(service, "username_exists", return_value=False):
            with patch(
                "app.services.UserResponse.model_validate", return_value=sample_user_response
            ) as mock_validate:
                result = await service.create_user(user_data)

                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()
                mock_validate.assert_called_once()
                assert result.email == sample_user_response.email

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, mock_db_session):
        existing_user = User(
            id=1,
            firebase_uid="existing",
            email="test@example.com",
            name="Existing",
            username="existing",
            created_at=datetime.now(),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=existing_user)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        user_data = UserCreate(
            firebase_uid="test_uid", email="test@example.com", name="Test", username="test"
        )

        with pytest.raises(ValidationException, match="already exists"):
            await service.create_user(user_data)

    @pytest.mark.asyncio
    async def test_create_user_username_taken(self, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        user_data = UserCreate(
            firebase_uid="test_uid",
            email="test@example.com",
            name="Test User",
            username="takenusername",
        )

        with patch.object(service, "username_exists", return_value=True):
            with pytest.raises(ValidationException, match="Username already taken"):
                await service.create_user(user_data)


class TestUserServiceRead:
    @pytest.mark.asyncio
    async def test_get_users_paginated(self, mock_db_session):
        with patch("app.services.paginate", new_callable=AsyncMock) as mock_paginate:
            mock_page = MagicMock()
            mock_page.items = []
            mock_paginate.return_value = mock_page

            service = UserService(mock_db_session)
            result = await service.get_users_paginated()

            mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_db_session, sample_user_response):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Test User",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.UserResponse.model_validate", return_value=sample_user_response):
            with patch("app.services.verify_resource_ownership"):
                service = UserService(mock_db_session)
                result = await service.get_user_by_id(
                    "test_firebase_uid_123", "test_firebase_uid_123"
                )

                assert result.firebase_uid == "test_firebase_uid_123"

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.verify_resource_ownership"):
            service = UserService(mock_db_session)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get_user_by_id("nonexistent_uid", "nonexistent_uid")

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, mock_db_session, sample_user_response):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Test User",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.UserResponse.model_validate", return_value=sample_user_response):
            with patch("app.services.verify_resource_ownership"):
                service = UserService(mock_db_session)
                result = await service.get_user_by_email(
                    "test@example.com", "test_firebase_uid_123"
                )

                assert result.firebase_uid == "test_firebase_uid_123"

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)

        with pytest.raises(EntityNotFoundException, match="not found"):
            await service.get_user_by_email("nonexistent@example.com", "test_uid")


class TestUserServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_db_session, sample_user_response):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Original Name",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.UserResponse.model_validate", return_value=sample_user_response):
            with patch("app.services.verify_resource_ownership"):
                service = UserService(mock_db_session)
                update_data = UserUpdate(name="Updated Name")

                result = await service.update_user(
                    "test_firebase_uid_123", update_data, "test_firebase_uid_123"
                )

                mock_db_session.commit.assert_called_once()
                mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.verify_resource_ownership"):
            service = UserService(mock_db_session)
            update_data = UserUpdate(name="Updated Name")

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update_user("nonexistent_uid", update_data, "nonexistent_uid")

    @pytest.mark.asyncio
    async def test_update_user_username_taken(self, mock_db_session):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="User",
            username="myusername",
            created_at=datetime.now(),
        )

        another_user = User(
            id=2,
            firebase_uid="another_uid",
            email="another@example.com",
            name="Another User",
            username="takenusername",
            created_at=datetime.now(),
        )

        call_count = [0]

        async def mock_execute_side_effect(stmt):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                result.scalar_one_or_none = Mock(return_value=user)
            else:
                result.scalar_one_or_none = Mock(return_value=another_user)
            return result

        mock_db_session.execute.side_effect = mock_execute_side_effect

        with patch("app.services.verify_resource_ownership"):
            service = UserService(mock_db_session)
            update_data = UserUpdate(username="takenusername")

            with pytest.raises(ValidationException, match="Username already taken"):
                await service.update_user(
                    "test_firebase_uid_123", update_data, "test_firebase_uid_123"
                )


class TestUserServiceImage:
    @pytest.mark.asyncio
    async def test_upload_user_image_success(self, mock_db_session):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Test User",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        mock_file = MagicMock()
        mock_file.filename = "test.jpg"
        mock_file.content_type = "image/jpeg"

        with patch("app.services.verify_resource_ownership"):
            with patch(
                "app.services.sync_model_image",
                return_value={"image_url": "https://example.com/new.jpg"},
            ):
                service = UserService(mock_db_session)

                result = await service.upload_user_image(
                    "test_firebase_uid_123", mock_file, "test_firebase_uid_123"
                )

                assert "image_url" in result

    @pytest.mark.asyncio
    async def test_delete_user_image_success(self, mock_db_session):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Test User",
            username="testuser",
            profile_image_url="https://storage.example.com/image.jpg",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.verify_resource_ownership"):
            with patch("app.services.CloudStorageService") as mock_cloud_class:
                mock_instance = MagicMock()
                mock_cloud_class.return_value = mock_instance

                service = UserService(mock_db_session)
                await service.delete_user_image("test_firebase_uid_123", "test_firebase_uid_123")

                mock_instance.delete_image.assert_called_once()
                mock_db_session.commit.assert_called_once()


class TestUserServiceSearch:
    @pytest.mark.asyncio
    async def test_search_users_found(self, mock_db_session, sample_user_response):
        user = User(
            id=1,
            firebase_uid="test_uid",
            email="test@example.com",
            name="Test User",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_scalars = MagicMock()
        mock_scalars.all = Mock(return_value=[user])
        mock_result = MagicMock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        result = await service.search_users("test")

        assert len(result.users) == 1

    @pytest.mark.asyncio
    async def test_search_users_not_found(self, mock_db_session):
        mock_scalars = MagicMock()
        mock_scalars.all = Mock(return_value=[])
        mock_result = MagicMock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        result = await service.search_users("nonexistent")

        assert len(result.users) == 0


class TestUserServiceSync:
    @pytest.mark.asyncio
    async def test_sync_firebase_user_new_user(self, mock_db_session, sample_user_response):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        with patch.object(UserService, "create_user", return_value=sample_user_response):
            service = UserService(mock_db_session)

            result = await service.sync_firebase_user(
                "firebase_uid_123", {"email": "firebase@example.com", "name": "Firebase User"}
            )

            assert result.firebase_uid == sample_user_response.firebase_uid

    @pytest.mark.asyncio
    async def test_sync_firebase_user_existing(self, mock_db_session, sample_user_response):
        user = User(
            id=1,
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Test User",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        with patch("app.services.UserResponse.model_validate", return_value=sample_user_response):
            service = UserService(mock_db_session)

            result = await service.sync_firebase_user(
                "test_firebase_uid_123", {"email": "test@example.com", "name": "Updated"}
            )

            assert result.firebase_uid == "test_firebase_uid_123"

    @pytest.mark.asyncio
    async def test_sync_firebase_user_missing_email(self, mock_db_session):
        service = UserService(mock_db_session)

        with pytest.raises(ValidationException, match="Email is required"):
            await service.sync_firebase_user("firebase_uid_123", {"name": "Firebase User"})


class TestUsernameGeneration:
    def test_generate_username_from_email_simple(self):
        email = "testuser@example.com"
        username = generate_username_from_email(email)

        assert username.startswith("testuser")
        assert len(username) == len("testuser") + 3

    def test_generate_username_from_email_with_dots(self):
        email = "test.user@example.com"
        username = generate_username_from_email(email)

        assert "test" in username
        assert "user" in username
        assert "." not in username

    def test_generate_username_from_email_with_special_chars(self):
        email = "user+tag@example.com"
        username = generate_username_from_email(email)

        assert "+" not in username

    def test_generate_username_from_email_long_username(self):
        email = "verylongusername@example.com"
        username = generate_username_from_email(email)

        assert len(username) <= 23

    def test_generate_username_random_suffix(self):
        email = "test@example.com"
        username1 = generate_username_from_email(email)
        username2 = generate_username_from_email(email)

        assert username1 != username2


class TestUsernameExists:
    @pytest.mark.asyncio
    async def test_username_exists_true(self, mock_db_session):
        user = User(
            id=1,
            firebase_uid="test_uid",
            email="test@example.com",
            name="Test",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=user)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        exists = await service.username_exists("testuser")

        assert exists is True

    @pytest.mark.asyncio
    async def test_username_exists_false(self, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        exists = await service.username_exists("nonexistent_user")

        assert exists is False

    @pytest.mark.asyncio
    async def test_username_exists_with_exclude_user_id(self, mock_db_session):
        different_user = User(
            id=2,
            firebase_uid="different_uid",
            email="different@example.com",
            name="Different",
            username="testuser",
            created_at=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=different_user)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        exists = await service.username_exists("testuser", exclude_user_id="my_uid")

        assert exists is True

    @pytest.mark.asyncio
    async def test_username_exists_with_exclude_same_user(self, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        service = UserService(mock_db_session)
        exists = await service.username_exists("testuser", exclude_user_id="my_uid")

        assert exists is False
