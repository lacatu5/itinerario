from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.schemas import UserCreate


class TestCreateUserEndpoint:
    @pytest.mark.asyncio
    async def test_create_user_success(self, client: AsyncClient):
        response = await client.post(
            "/api/users/",
            json={
                "firebase_uid": "test_uid_123",
                "email": "newuser@example.com",
                "name": "New User",
                "username": "newuser123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["firebase_uid"] == "test_uid_123"
        assert data["name"] == "New User"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient, db_session):
        from app.services import UserService

        service = UserService(db_session)
        await service.create_user(
            UserCreate(
                firebase_uid="uid1", email="duplicate@example.com", name="User 1", username="user1"
            )
        )

        response = await client.post(
            "/api/users/",
            json={
                "firebase_uid": "uid2",
                "email": "duplicate@example.com",
                "name": "User 2",
                "username": "user2",
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/users/",
            json={
                "firebase_uid": "test_uid",
                "email": "invalid-email",
                "name": "Test",
                "username": "test",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/users/", json={"firebase_uid": "test_uid"})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_short_username(self, client: AsyncClient):
        response = await client.post(
            "/api/users/",
            json={
                "firebase_uid": "test_uid",
                "email": "test@example.com",
                "name": "Test",
                "username": "ab",
            },
        )

        assert response.status_code == 422


class TestGetUserEndpoint:
    @pytest.mark.asyncio
    async def test_get_user_success(self, client: AsyncClient, db_session, auth_user_id: str):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id,
                email="test@example.com",
                name="Test User",
                username="testuser",
            )
        )

        response = await client.get(f"/api/users/{user.firebase_uid}")

        assert response.status_code == 200
        data = response.json()
        assert data["firebase_uid"] == auth_user_id
        assert data["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient, auth_user_id: str):
        response = await client.get(f"/api/users/{auth_user_id}_nonexistent")

        assert response.status_code in (403, 404)


class TestGetUserByEmailEndpoint:
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, client: AsyncClient, db_session, auth_user_id: str
    ):
        from app.services import UserService

        email = "test@example.com"
        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id, email=email, name="Test User", username="testuser"
            )
        )

        response = await client.get(f"/api/users/email/{email}")

        assert response.status_code == 200
        data = response.json()
        assert data["firebase_uid"] == auth_user_id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, client: AsyncClient):
        response = await client.get("/api/users/email/nonexistent@example.com")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateUserEndpoint:
    @pytest.mark.asyncio
    async def test_update_user_success(self, client: AsyncClient, db_session, auth_user_id: str):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id,
                email="test@example.com",
                name="Original Name",
                username="testuser",
            )
        )

        response = await client.put(
            f"/api/users/{user.firebase_uid}", json={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient, auth_user_id: str):
        response = await client.put(
            f"/api/users/{auth_user_id}_nonexistent", json={"name": "Updated"}
        )

        assert response.status_code in (403, 404)

    @pytest.mark.asyncio
    async def test_update_user_with_username_taken(
        self, client: AsyncClient, db_session, auth_user_id: str
    ):
        from app.services import UserService

        service = UserService(db_session)
        user1 = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id,
                email="user1@example.com",
                name="User 1",
                username="user1",
            )
        )
        await service.create_user(
            UserCreate(
                firebase_uid="other_user_uid",
                email="user2@example.com",
                name="User 2",
                username="user2",
            )
        )

        response = await client.put(f"/api/users/{user1.firebase_uid}", json={"username": "user2"})

        assert response.status_code == 400
        assert "already taken" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_user_partial(self, client: AsyncClient, db_session, auth_user_id: str):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id,
                email="test@example.com",
                name="Test User",
                username="testuser",
            )
        )

        response = await client.put(f"/api/users/{user.firebase_uid}", json={"name": "New Name"})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["username"] == "testuser"


class TestListUsersEndpoint:
    @pytest.mark.asyncio
    async def test_list_users_default_pagination(self, client: AsyncClient):
        response = await client.get("/api/users/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_users_custom_pagination(self, client: AsyncClient):
        response = await client.get("/api/users/?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10

    @pytest.mark.asyncio
    async def test_list_users_with_multiple_users(self, client: AsyncClient, db_session):
        from app.services import UserService

        service = UserService(db_session)
        initial_count = len((await service.get_users_paginated()).items)

        for i in range(5):
            await service.create_user(
                UserCreate(
                    firebase_uid=f"list_test_user_{i}",
                    email=f"listuser{i}@example.com",
                    name=f"User {i}",
                    username=f"listuser{i}",
                )
            )

        response = await client.get("/api/users/?skip=0&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 3


class TestSearchUsersEndpoint:
    @pytest.mark.asyncio
    async def test_search_users_by_name(self, client: AsyncClient, db_session):
        from app.services import UserService

        service = UserService(db_session)
        await service.create_user(
            UserCreate(
                firebase_uid="search_test_uid",
                email="john@example.com",
                name="John Doe",
                username="johndoe",
            )
        )

        response = await client.get("/api/users/search?query=John")

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) > 0

    @pytest.mark.asyncio
    async def test_search_users_by_username(self, client: AsyncClient, db_session):
        from app.services import UserService

        service = UserService(db_session)
        await service.create_user(
            UserCreate(
                firebase_uid="search_test_uid2",
                email="john@example.com",
                name="John Doe",
                username="johndoe",
            )
        )

        response = await client.get("/api/users/search?query=john")

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) > 0

    @pytest.mark.asyncio
    async def test_search_users_no_results(self, client: AsyncClient):
        response = await client.get("/api/users/search?query=NonExistentName123")

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 0

    @pytest.mark.asyncio
    async def test_search_users_missing_query(self, client: AsyncClient):
        response = await client.get("/api/users/search")

        assert response.status_code == 422


class TestUploadImageEndpoint:
    @pytest.mark.asyncio
    async def test_upload_image_success(self, client: AsyncClient, db_session, auth_user_id: str):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id,
                email="test@example.com",
                name="Test User",
                username="testuser",
            )
        )

        file_content = b"fake image content"

        with patch("app.services.sync_model_image") as mock_sync:
            mock_sync.return_value = {"image_url": "https://storage.example.com/test.jpg"}

            response = await client.post(
                f"/api/users/{user.firebase_uid}/upload-image",
                files={"file": ("test.jpg", file_content, "image/jpeg")},
            )

            assert response.status_code == 200
            data = response.json()
            assert "image_url" in data

    @pytest.mark.asyncio
    async def test_upload_image_unauthorized(self, client: AsyncClient, db_session):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid="owner_uid", email="owner@example.com", name="Owner", username="owner"
            )
        )

        file_content = b"fake image"

        response = await client.post(
            f"/api/users/{user.firebase_uid}/upload-image",
            files={"file": ("test.jpg", file_content, "image/jpeg")},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_upload_image_user_not_found(self, client: AsyncClient, auth_user_id: str):
        file_content = b"fake image"

        response = await client.post(
            f"/api/users/{auth_user_id}_nonexistent/upload-image",
            files={"file": ("test.jpg", file_content, "image/jpeg")},
        )

        assert response.status_code == 403


class TestDeleteImageEndpoint:
    @pytest.mark.asyncio
    async def test_delete_image_success(self, client: AsyncClient, db_session, auth_user_id: str):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid=auth_user_id,
                email="test@example.com",
                name="Test User",
                username="testuser",
            )
        )

        with patch("app.services.CloudStorageService") as mock_cloud:
            mock_instance = MagicMock()
            mock_cloud.return_value = mock_instance

            response = await client.delete(f"/api/users/{user.firebase_uid}/image")

            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_image_unauthorized(self, client: AsyncClient, db_session):
        from app.services import UserService

        service = UserService(db_session)
        user = await service.create_user(
            UserCreate(
                firebase_uid="owner_uid", email="owner@example.com", name="Owner", username="owner"
            )
        )

        response = await client.delete(f"/api/users/{user.firebase_uid}/image")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_image_user_not_found(self, client: AsyncClient, auth_user_id: str):
        response = await client.delete(f"/api/users/{auth_user_id}_nonexistent/image")

        assert response.status_code == 403
