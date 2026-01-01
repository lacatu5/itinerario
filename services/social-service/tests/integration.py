from unittest.mock import MagicMock, patch

import pytest

from app.models import Follow, Like


class TestLikeEndpoints:
    @pytest.mark.asyncio
    async def test_like_itinerary_success(self, client):
        def mock_save(self):
            if not self.id:
                self.id = f"{self.itinerary_id}_{self.user_id}"

        with patch.object(Like.collection, "get", return_value=None):
            with patch.object(Like, "save", mock_save):
                response = await client.post(
                    "/api/social/itineraries/itinerary123/like", json={"comment": "Great trip!"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["itinerary_id"] == "itinerary123"

    @pytest.mark.asyncio
    async def test_like_itinerary_already_liked(self, client):
        mock_existing = MagicMock()
        with patch.object(Like.collection, "get", return_value=mock_existing):
            response = await client.post(
                "/api/social/itineraries/itinerary123/like", json={"comment": "Great trip!"}
            )

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unlike_itinerary_success(self, client):
        mock_like = MagicMock()
        mock_like.user_id = "test_firebase_uid_123"
        with patch.object(Like.collection, "get", return_value=mock_like):
            with patch.object(Like.collection, "delete"):
                response = await client.delete("/api/social/itineraries/itinerary123/like")

                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_unlike_itinerary_not_found(self, client):
        with patch.object(Like.collection, "get", return_value=None):
            response = await client.delete("/api/social/itineraries/itinerary123/like")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_like_comment_success(self, client):
        def create_mock_like():
            mock_like = MagicMock()
            mock_like.user_id = "test_firebase_uid_123"
            mock_like.itinerary_id = "itinerary123"
            mock_like.id = "itinerary123_test_firebase_uid_123"
            mock_like.comment = "Updated comment"
            mock_like.created_at = None
            mock_like.updated_at = None
            return mock_like

        with patch.object(Like.collection, "get", side_effect=lambda x: create_mock_like()):
            with patch.object(Like, "save"):
                response = await client.put(
                    "/api/social/itineraries/itinerary123/like", json={"comment": "Updated comment"}
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_like_comment_not_found(self, client):
        with patch.object(Like.collection, "get", return_value=None):
            response = await client.put(
                "/api/social/itineraries/itinerary123/like", json={"comment": "Updated comment"}
            )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_itinerary_likes_success(self, client):
        with patch(
            "app.services.BaseFirestoreService.paginate",
            return_value={"items": [], "next_cursor": None, "has_more": False},
        ):
            response = await client.get("/api/social/itineraries/itinerary123/likes")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "next_cursor" in data
            assert "has_more" in data

    @pytest.mark.asyncio
    async def test_get_itinerary_likes_with_pagination(self, client):
        with patch(
            "app.services.BaseFirestoreService.paginate",
            return_value={"items": [], "next_cursor": "cursor_123", "has_more": True},
        ):
            response = await client.get(
                "/api/social/itineraries/itinerary123/likes?limit=50&cursor=cursor_123"
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_itinerary_stats_success(self, client):
        with patch("app.services.BaseFirestoreService.list", return_value=[]):
            response = await client.get("/api/social/itineraries/itinerary123/stats")

            assert response.status_code == 200
            data = response.json()
            assert "total_likes" in data
            assert "total_comments" in data

    @pytest.mark.asyncio
    async def test_check_like_status_liked(self, client):
        def create_mock_like():
            mock_like = MagicMock()
            mock_like.itinerary_id = "itinerary123"
            mock_like.user_id = "test_firebase_uid_123"
            mock_like.id = "itinerary123_test_firebase_uid_123"
            mock_like.comment = "Great!"
            mock_like.created_at = None
            mock_like.updated_at = None
            return mock_like

        with patch(
            "app.services.Like.collection.get",
            side_effect=lambda x: create_mock_like()
            if x == "itinerary123_test_firebase_uid_123"
            else None,
        ):
            with patch("app.services.BaseFirestoreService.list", return_value=[]):
                response = await client.get("/api/social/itineraries/itinerary123/like-status")

                assert response.status_code == 200
                data = response.json()
                assert "liked" in data
                assert "total_likes" in data

    @pytest.mark.asyncio
    async def test_check_like_status_not_liked(self, client):
        with patch("app.services.Like.collection.get", return_value=None):
            with patch("app.services.BaseFirestoreService.list", return_value=[]):
                response = await client.get("/api/social/itineraries/itinerary123/like-status")

                assert response.status_code == 200
                data = response.json()
                assert data["liked"] is False


class TestFollowEndpoints:
    @pytest.mark.asyncio
    async def test_follow_user_success(self, client):
        def mock_save(self):
            if not self.id:
                self.id = f"{self.follower_id}_{self.following_id}"

        with patch.object(Follow, "save", mock_save):
            response = await client.post(
                "/api/social/follow",
                json={"follower_id": "test_firebase_uid_123", "following_id": "user456"},
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_follow_user_validation_error(self, client):
        response = await client.post(
            "/api/social/follow", json={"follower_id": "user123", "following_id": "user123"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_followers_success(self, client):
        with patch(
            "app.services.BaseFirestoreService.paginate",
            return_value={"items": [], "next_cursor": None, "has_more": False},
        ):
            response = await client.get("/api/social/followers/user123")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "next_cursor" in data
            assert "has_more" in data

    @pytest.mark.asyncio
    async def test_get_followers_with_pagination(self, client):
        with patch(
            "app.services.BaseFirestoreService.paginate",
            return_value={"items": [], "next_cursor": "cursor_abc", "has_more": True},
        ):
            response = await client.get("/api/social/followers/user123?limit=30&cursor=cursor_abc")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_following_success(self, client):
        with patch(
            "app.services.BaseFirestoreService.paginate",
            return_value={"items": [], "next_cursor": None, "has_more": False},
        ):
            response = await client.get("/api/social/following/user123")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "next_cursor" in data
            assert "has_more" in data

    @pytest.mark.asyncio
    async def test_get_following_with_pagination(self, client):
        with patch(
            "app.services.BaseFirestoreService.paginate",
            return_value={"items": [], "next_cursor": "cursor_xyz", "has_more": True},
        ):
            response = await client.get("/api/social/following/user123?limit=40&cursor=cursor_xyz")

            assert response.status_code == 200


class TestCentrifugoTokenEndpoint:
    @pytest.mark.asyncio
    async def test_get_centrifugo_token_success(self, client):
        response = await client.post("/api/social/centrifugo-token")

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "ws_url" in data
        assert "user_id" in data


class TestEndpointValidation:
    @pytest.mark.asyncio
    async def test_like_itinerary_with_empty_comment(self, client):
        def mock_save(self):
            if not self.id:
                self.id = f"{self.itinerary_id}_{self.user_id}"

        with patch.object(Like.collection, "get", return_value=None):
            with patch.object(Like, "save", mock_save):
                response = await client.post(
                    "/api/social/itineraries/itinerary123/like", json={"comment": None}
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_like_with_empty_comment(self, client):
        def create_mock_like():
            mock_like = MagicMock()
            mock_like.user_id = "test_firebase_uid_123"
            mock_like.itinerary_id = "itinerary123"
            mock_like.id = "itinerary123_test_firebase_uid_123"
            mock_like.comment = None
            mock_like.created_at = None
            mock_like.updated_at = None
            return mock_like

        with patch.object(Like.collection, "get", side_effect=lambda x: create_mock_like()):
            with patch.object(Like, "save"):
                response = await client.put(
                    "/api/social/itineraries/itinerary123/like", json={"comment": None}
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_likes_with_invalid_limit(self, client):
        response = await client.get("/api/social/itineraries/itinerary123/likes?limit=101")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_likes_with_negative_limit(self, client):
        response = await client.get("/api/social/itineraries/itinerary123/likes?limit=0")

        assert response.status_code == 422


class TestOwnershipValidation:
    @pytest.mark.asyncio
    async def test_unlike_like_wrong_user(self, client):
        mock_like = MagicMock()
        mock_like.user_id = "different_user"
        with patch.object(Like.collection, "get", return_value=mock_like):
            response = await client.delete("/api/social/itineraries/itinerary123/like")

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_like_wrong_user(self, client):
        mock_like = MagicMock()
        mock_like.user_id = "different_user"
        with patch.object(Like.collection, "get", return_value=mock_like):
            response = await client.put(
                "/api/social/itineraries/itinerary123/like", json={"comment": "Updated"}
            )

            assert response.status_code == 403
