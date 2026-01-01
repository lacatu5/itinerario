from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.services import LikeService, FollowService
from core.exceptions import EntityNotFoundException, ValidationException


class TestLikeServiceCreate:
    @pytest.mark.asyncio
    async def test_add_like_success(self, mock_centrifugo_client):
        from app.models import Like

        def mock_save(self):
            if not self.id:
                self.id = f"{self.itinerary_id}_{self.user_id}"

        with patch.object(Like.collection, "get", return_value=None):
            with patch.object(Like, "save", mock_save):
                service = LikeService(mock_centrifugo_client)
                result = await service.add_like("itinerary123", "user123", "Great trip!")

                assert result is not None
                assert result.itinerary_id == "itinerary123"
                assert result.user_id == "user123"
                assert result.comment == "Great trip!"

    @pytest.mark.asyncio
    async def test_add_like_already_liked(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_existing = MagicMock()
            mock_like_class.collection.get.return_value = mock_existing

            service = LikeService(mock_centrifugo_client)

            with pytest.raises(ValidationException, match="already liked"):
                await service.add_like("itinerary123", "user123")


class TestLikeServiceRead:
    @pytest.mark.asyncio
    async def test_get_likes_for_itinerary(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.paginate = MagicMock(
            return_value={"items": [], "next_cursor": None, "has_more": False}
        )

        result = await service.get_likes_for_itinerary("itinerary123")

        assert hasattr(result, "items")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")

    @pytest.mark.asyncio
    async def test_get_like_count(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.list = MagicMock(return_value=[])

        result = await service.get_like_count_for_itinerary("itinerary123")

        assert result == 0

    @pytest.mark.asyncio
    async def test_check_user_liked(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_like = MagicMock()
            mock_like_class.collection.get.return_value = mock_like

            service = LikeService(mock_centrifugo_client)
            result = await service.check_user_liked_itinerary("itinerary123", "user123")

            assert result is True

    @pytest.mark.asyncio
    async def test_get_like_status(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.check_user_liked_itinerary = AsyncMock(return_value=True)
        service.get_like_count_for_itinerary = AsyncMock(return_value=5)
        service.get_like_for_user = AsyncMock(return_value=None)

        result = await service.get_like_status("itinerary123", "user123")

        assert result.liked is True
        assert result.total_likes == 5


class TestLikeServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_like_comment_success(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_like = MagicMock()
            mock_like.configure_mock(
                id="like123",
                itinerary_id="itinerary123",
                user_id="user123",
                comment="Updated comment",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            mock_like_class.collection.get.return_value = mock_like

            service = LikeService(mock_centrifugo_client)
            result = await service.update_like_comment("itinerary123", "user123", "Updated comment")

            assert result is not None

    @pytest.mark.asyncio
    async def test_update_like_not_found(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_like_class.collection.get.return_value = None

            service = LikeService(mock_centrifugo_client)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update_like_comment("itinerary123", "user123", "Updated")


class TestLikeServiceDelete:
    @pytest.mark.asyncio
    async def test_remove_like_success(self, mock_centrifugo_client):
        with (
            patch("app.services.Like.collection.get") as mock_get,
            patch("app.services.Like.collection.delete") as mock_delete,
        ):
            mock_like = MagicMock()
            mock_like.user_id = "user123"
            mock_get.return_value = mock_like

            service = LikeService(mock_centrifugo_client)
            await service.remove_like("itinerary123", "user123")

            mock_delete.assert_called_once_with("itinerary123_user123")

    @pytest.mark.asyncio
    async def test_remove_like_not_found(self, mock_centrifugo_client):
        with patch("app.services.Like.collection.get") as mock_get:
            mock_get.return_value = None

            service = LikeService(mock_centrifugo_client)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.remove_like("itinerary123", "user123")


class TestLikeServicePublish:
    @pytest.mark.asyncio
    async def test_publish_new_like(self, mock_centrifugo_client):
        mock_centrifugo_client.publish = AsyncMock()

        service = LikeService(mock_centrifugo_client)
        mock_like = MagicMock()
        mock_like.model_dump = Mock(return_value={"id": "like123"})

        await service.publish_new_like("itinerary123", "user123", mock_like)

        mock_centrifugo_client.publish.assert_called_once()


class TestFollowServiceCreate:
    @pytest.mark.asyncio
    async def test_follow_user_success(self, mock_centrifugo_client):
        with patch("app.services.Follow") as mock_follow_class:
            mock_follow = MagicMock()
            mock_follow.id = "follow123"
            mock_follow_class.return_value = mock_follow

            service = FollowService(mock_centrifugo_client)
            result = await service.follow_user("follower123", "following123")

            assert result is not None


class TestFollowServiceRead:
    @pytest.mark.asyncio
    async def test_get_followers(self, mock_centrifugo_client):
        service = FollowService(mock_centrifugo_client)
        service.paginate = MagicMock(
            return_value={"items": [], "next_cursor": None, "has_more": False}
        )

        result = await service.get_followers("user123")

        assert hasattr(result, "items")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")

    @pytest.mark.asyncio
    async def test_get_following(self, mock_centrifugo_client):
        service = FollowService(mock_centrifugo_client)
        service.paginate = MagicMock(
            return_value={"items": [], "next_cursor": None, "has_more": False}
        )

        result = await service.get_following("user123")

        assert hasattr(result, "items")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")


class TestFollowServicePublish:
    @pytest.mark.asyncio
    async def test_publish_new_follower(self, mock_centrifugo_client):
        mock_centrifugo_client.publish = AsyncMock()

        service = FollowService(mock_centrifugo_client)
        await service.publish_new_follower("follower123", "following123")

        mock_centrifugo_client.publish.assert_called_once()


class TestLikeServiceEdgeCases:
    @pytest.mark.asyncio
    async def test_add_like_without_centrifugo(self):
        from app.models import Like

        def mock_save(self):
            if not self.id:
                self.id = f"{self.itinerary_id}_{self.user_id}"

        with patch.object(Like.collection, "get", return_value=None):
            with patch.object(Like, "save", mock_save):
                service = LikeService(None)
                result = await service.add_like("itinerary123", "user123", "Great trip!")

                assert result is not None

    @pytest.mark.asyncio
    async def test_publish_new_like_without_centrifugo(self):
        service = LikeService(None)
        mock_like = MagicMock()
        mock_like.model_dump = Mock(return_value={"id": "like123"})

        await service.publish_new_like("itinerary123", "user123", mock_like)

    @pytest.mark.asyncio
    async def test_publish_new_like_failure(self, mock_centrifugo_client):
        mock_centrifugo_client.publish = AsyncMock(side_effect=Exception("Publish failed"))

        service = LikeService(mock_centrifugo_client)
        mock_like = MagicMock()
        mock_like.model_dump = Mock(return_value={"id": "like123"})

        await service.publish_new_like("itinerary123", "user123", mock_like)

    @pytest.mark.asyncio
    async def test_check_user_not_liked(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_like_class.collection.get.return_value = None

            service = LikeService(mock_centrifugo_client)
            result = await service.check_user_liked_itinerary("itinerary123", "user123")

            assert result is False

    @pytest.mark.asyncio
    async def test_get_like_status_not_liked(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.check_user_liked_itinerary = AsyncMock(return_value=False)
        service.get_like_count_for_itinerary = AsyncMock(return_value=5)
        service.get_like_for_user = AsyncMock(return_value=None)

        result = await service.get_like_status("itinerary123", "user123")

        assert result.liked is False
        assert result.total_likes == 5


class TestFollowServiceEdgeCases:
    @pytest.mark.asyncio
    async def test_publish_new_follower_without_centrifugo(self):
        service = FollowService(None)
        await service.publish_new_follower("follower123", "following123")

    @pytest.mark.asyncio
    async def test_publish_new_follower_failure(self, mock_centrifugo_client):
        mock_centrifugo_client.publish = AsyncMock(side_effect=Exception("Publish failed"))

        service = FollowService(mock_centrifugo_client)
        await service.publish_new_follower("follower123", "following123")


class TestLikeServiceGetLikeForUser:
    @pytest.mark.asyncio
    async def test_get_like_for_user_found(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_like = MagicMock()
            mock_like.itinerary_id = "itinerary123"
            mock_like.user_id = "user123"
            mock_like.comment = "Great!"
            mock_like.id = "itinerary123_user123"
            mock_like_class.collection.get.return_value = mock_like

            service = LikeService(mock_centrifugo_client)
            result = await service.get_like_for_user("itinerary123", "user123")

            assert result is not None
            assert result.itinerary_id == "itinerary123"
            assert result.user_id == "user123"

    @pytest.mark.asyncio
    async def test_get_like_for_user_not_found(self, mock_centrifugo_client):
        with patch("app.services.Like") as mock_like_class:
            mock_like_class.collection.get.return_value = None

            service = LikeService(mock_centrifugo_client)
            result = await service.get_like_for_user("itinerary123", "user123")

            assert result is None


class TestLikeServiceGetItineraryStats:
    @pytest.mark.asyncio
    async def test_get_itinerary_stats_with_comments(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)

        mock_likes = [
            MagicMock(comment="Comment 1"),
            MagicMock(comment="Comment 2"),
            MagicMock(comment=None),
        ]
        service.list = MagicMock(return_value=mock_likes)

        result = await service.get_itinerary_stats("itinerary123")

        assert result.total_likes == 3
        assert result.total_comments == 2

    @pytest.mark.asyncio
    async def test_get_itinerary_stats_no_comments(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)

        mock_likes = [MagicMock(comment=None), MagicMock(comment=None)]
        service.list = MagicMock(return_value=mock_likes)

        result = await service.get_itinerary_stats("itinerary123")

        assert result.total_likes == 2
        assert result.total_comments == 0

    @pytest.mark.asyncio
    async def test_get_itinerary_stats_empty(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.list = MagicMock(return_value=[])

        result = await service.get_itinerary_stats("itinerary123")

        assert result.total_likes == 0
        assert result.total_comments == 0


class TestLikeServiceRemoveLikeOwnership:
    @pytest.mark.asyncio
    async def test_remove_like_wrong_user(self, mock_centrifugo_client):
        from core.exceptions import AuthorizationException

        with patch("app.services.Like.collection.get") as mock_get:
            mock_like = MagicMock()
            mock_like.user_id = "different_user"
            mock_get.return_value = mock_like

            service = LikeService(mock_centrifugo_client)

            with pytest.raises(AuthorizationException):
                await service.remove_like("itinerary123", "user123")


class TestLikeServiceUpdateCommentOwnership:
    @pytest.mark.asyncio
    async def test_update_like_comment_wrong_user(self, mock_centrifugo_client):
        from core.exceptions import AuthorizationException

        with patch("app.services.Like") as mock_like_class:
            mock_like = MagicMock()
            mock_like.user_id = "different_user"
            mock_like_class.collection.get.return_value = mock_like

            service = LikeService(mock_centrifugo_client)

            with pytest.raises(AuthorizationException):
                await service.update_like_comment("itinerary123", "user123", "Updated")


class TestLikeServiceGetLikeCountErrors:
    @pytest.mark.asyncio
    async def test_get_like_count_exception_handling(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.list = MagicMock(side_effect=Exception("Database error"))

        result = await service.get_like_count_for_itinerary("itinerary123")

        assert result == 0


class TestLikeServiceCheckUserLikedErrors:
    @pytest.mark.asyncio
    async def test_check_user_liked_exception_handling(self, mock_centrifugo_client):
        with patch("app.services.Like.collection.get", side_effect=Exception("Database error")):
            service = LikeService(mock_centrifugo_client)
            result = await service.check_user_liked_itinerary("itinerary123", "user123")

            assert result is False


class TestLikeServiceGetLikeStatusWithComment:
    @pytest.mark.asyncio
    async def test_get_like_status_with_comment(self, mock_centrifugo_client):
        from app.schemas import LikeResponse

        service = LikeService(mock_centrifugo_client)
        service.check_user_liked_itinerary = AsyncMock(return_value=True)
        service.get_like_count_for_itinerary = AsyncMock(return_value=5)

        mock_like_response = LikeResponse(
            id="itinerary123_user123",
            itinerary_id="itinerary123",
            user_id="user123",
            comment="Amazing trip!",
            created_at=None,
            updated_at=None,
        )
        service.get_like_for_user = AsyncMock(return_value=mock_like_response)

        result = await service.get_like_status("itinerary123", "user123")

        assert result.liked is True
        assert result.total_likes == 5
        assert result.comment == "Amazing trip!"


class TestFollowServiceGetFollowersWithPagination:
    @pytest.mark.asyncio
    async def test_get_followers_with_custom_limit(self, mock_centrifugo_client):
        service = FollowService(mock_centrifugo_client)
        service.paginate = MagicMock(
            return_value={"items": [], "next_cursor": "next_cursor_123", "has_more": True}
        )

        result = await service.get_followers("user123", limit=50, cursor="cursor_123")

        assert hasattr(result, "items")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")


class TestFollowServiceGetFollowingWithPagination:
    @pytest.mark.asyncio
    async def test_get_following_with_custom_limit(self, mock_centrifugo_client):
        service = FollowService(mock_centrifugo_client)
        service.paginate = MagicMock(
            return_value={"items": [], "next_cursor": "next_cursor_456", "has_more": False}
        )

        result = await service.get_following("user123", limit=30, cursor="cursor_456")

        assert hasattr(result, "items")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")


class TestLikeServiceGetLikesWithPagination:
    @pytest.mark.asyncio
    async def test_get_likes_for_itinerary_with_custom_params(self, mock_centrifugo_client):
        service = LikeService(mock_centrifugo_client)
        service.paginate = MagicMock(
            return_value={"items": [], "next_cursor": "cursor_abc", "has_more": True}
        )

        result = await service.get_likes_for_itinerary(
            "itinerary123", limit=25, cursor="cursor_xyz"
        )

        assert hasattr(result, "items")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")


class TestSchemaValidations:
    def test_follow_create_cannot_follow_self(self):
        from pydantic import ValidationError
        from app.schemas import FollowCreate

        with pytest.raises(ValidationError, match="Cannot follow yourself"):
            FollowCreate(follower_id="user123", following_id="user123")

    def test_follow_create_success(self):
        from app.schemas import FollowCreate

        follow = FollowCreate(follower_id="user123", following_id="user456")

        assert follow.follower_id == "user123"
        assert follow.following_id == "user456"

    def test_like_create_empty_comment(self):
        from app.schemas import LikeCreate

        like = LikeCreate(comment=None)

        assert like.comment is None

    def test_like_create_with_comment(self):
        from app.schemas import LikeCreate

        like = LikeCreate(comment="Great trip!")

        assert like.comment == "Great trip!"

    def test_like_update_comment(self):
        from app.schemas import LikeUpdate

        update = LikeUpdate(comment="Updated comment")

        assert update.comment == "Updated comment"

    def test_like_update_no_comment(self):
        from app.schemas import LikeUpdate

        update = LikeUpdate()

        assert update.comment is None

    def test_like_status_response(self):
        from app.schemas import LikeStatusResponse

        status = LikeStatusResponse(liked=True, total_likes=5, comment="Amazing!", like=None)

        assert status.liked is True
        assert status.total_likes == 5
        assert status.comment == "Amazing!"

    def test_itinerary_stats(self):
        from app.schemas import ItineraryStats

        stats = ItineraryStats(total_likes=10, total_comments=5)

        assert stats.total_likes == 10
        assert stats.total_comments == 5
