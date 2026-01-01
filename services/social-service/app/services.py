from loguru import logger

from app.models import Follow, Like
from app.schemas import (
    FollowersListResponse,
    FollowResponse,
    ItineraryStats,
    LikeResponse,
    LikeStatusResponse,
)
from core.auth.ownership import verify_ownership
from core.exceptions import EntityNotFoundException, ValidationException
from core.firestore.models import BaseFirestoreService
from core.messaging.client import CentrifugoClient


class LikeService(BaseFirestoreService):
    def __init__(self, centrifugo_client: CentrifugoClient | None = None):
        super().__init__(Like, LikeResponse)
        self.centrifugo = centrifugo_client

    async def add_like(
        self, itinerary_id: str, user_id: str, comment: str | None = None
    ) -> LikeResponse:
        like_id = f"{itinerary_id}_{user_id}"
        existing_like = Like.collection.get(like_id)
        if existing_like:
            raise ValidationException("User has already liked this itinerary")

        like = Like()
        like.itinerary_id = itinerary_id
        like.user_id = user_id
        like.comment = comment if comment else None
        like.save()
        logger.info(f"Like added: itineraryId={itinerary_id}, userId={user_id}, comment={comment}")

        return LikeResponse.model_validate(like)

    async def publish_new_like(self, itinerary_id: str, user_id: str, like: LikeResponse):
        if not self.centrifugo:
            return
        try:
            await self.centrifugo.publish(
                f"social:user:{user_id}",
                {
                    "type": "new_like",
                    "itinerary_id": itinerary_id,
                    "like": like.model_dump(mode="json"),
                },
            )
        except Exception as e:
            logger.error(f"Failed to publish new like event: {e}")

    async def remove_like(self, itinerary_id: str, user_id: str) -> None:
        like_id = f"{itinerary_id}_{user_id}"
        like = Like.collection.get(like_id)
        if not like:
            raise EntityNotFoundException(f"Like {like_id} not found")
        verify_ownership(like.user_id, user_id, "like")
        Like.collection.delete(like_id)
        logger.info(f"Like removed: itinerary_id={itinerary_id}, user_id={user_id}")

    async def get_likes_for_itinerary(
        self, itinerary_id: str, limit: int | None = None, cursor: str | None = None
    ):
        from app.schemas import LikesListResponse

        if not limit:
            limit = 20

        result = self.paginate(
            filters={"itinerary_id": {"op": "==", "value": itinerary_id}},
            order_by="-created_at",
            limit=limit,
            cursor=cursor,
        )

        logger.info(f"Retrieved {len(result['items'])} likes for itinerary {itinerary_id}")
        return LikesListResponse(
            items=result["items"],
            next_cursor=result["next_cursor"],
            has_more=result["has_more"],
        )

    async def get_like_count_for_itinerary(self, itinerary_id: str) -> int:
        try:
            results = self.list(filters={"itinerary_id": {"op": "==", "value": itinerary_id}})
            count = len(results)
            logger.info(f"Like count for itinerary {itinerary_id}: {count}")
            return count
        except Exception as e:
            logger.opt(exception=True).error(
                f"Error getting like count for itinerary {itinerary_id}: {str(e)}"
            )
            return 0

    async def check_user_liked_itinerary(self, itinerary_id: str, user_id: str) -> bool:
        try:
            like_id = f"{itinerary_id}_{user_id}"
            like = Like.collection.get(like_id)
            return like is not None
        except Exception as e:
            logger.opt(exception=True).error(f"Error checking if user liked itinerary: {e}")
            return False

    async def update_like_comment(
        self, itinerary_id: str, user_id: str, comment: str | None
    ) -> LikeResponse:
        like_id = f"{itinerary_id}_{user_id}"
        like = Like.collection.get(like_id)
        if not like:
            raise EntityNotFoundException(f"Like {like_id} not found")

        verify_ownership(like.user_id, user_id, "like")

        like.comment = comment if comment else None
        like.save()
        logger.info(f"Like comment updated: itinerary_id={itinerary_id}, user_id={user_id}")

        return LikeResponse.model_validate(like)

    async def get_like_for_user(self, itinerary_id: str, user_id: str) -> LikeResponse | None:
        like_id = f"{itinerary_id}_{user_id}"
        like = Like.collection.get(like_id)
        return LikeResponse.model_validate(like) if like else None

    async def get_itinerary_stats(self, itinerary_id: str) -> ItineraryStats:
        results = self.list(filters={"itinerary_id": {"op": "==", "value": itinerary_id}})
        total_likes = len(results)
        total_comments = sum(1 for like in results if like.comment)
        return ItineraryStats(total_likes=total_likes, total_comments=total_comments)

    async def get_like_status(self, itinerary_id: str, user_id: str) -> LikeStatusResponse:
        has_liked = await self.check_user_liked_itinerary(itinerary_id, user_id)
        like_count = await self.get_like_count_for_itinerary(itinerary_id)
        like_details = await self.get_like_for_user(itinerary_id, user_id) if has_liked else None

        return LikeStatusResponse(
            liked=has_liked,
            total_likes=like_count,
            comment=like_details.comment if like_details else None,
            like=like_details,
        )


class FollowService(BaseFirestoreService):
    def __init__(self, centrifugo_client: CentrifugoClient | None = None):
        super().__init__(Follow, FollowResponse)
        self.centrifugo = centrifugo_client

    async def follow_user(self, follower_id: str, following_id: str) -> FollowResponse:
        follow = Follow()
        follow.follower_id = follower_id
        follow.following_id = following_id
        follow.save()
        logger.info(f"User {follower_id} is now following {following_id}")

        return FollowResponse.model_validate(follow)

    async def publish_new_follower(self, follower_id: str, following_id: str):
        if not self.centrifugo:
            return
        try:
            await self.centrifugo.publish(
                f"social:user:{following_id}",
                {
                    "type": "new_follower",
                    "follower_id": follower_id,
                    "following_id": following_id,
                },
            )
        except Exception as e:
            logger.error(f"Failed to publish new follower event: {e}")

    async def get_followers(
        self, user_id: str, limit: int | None = None, cursor: str | None = None
    ):
        if not limit:
            limit = 20

        result = self.paginate(
            filters={"following_id": {"op": "==", "value": user_id}},
            order_by="-created_at",
            limit=limit,
            cursor=cursor,
        )

        return FollowersListResponse(
            items=result["items"],
            next_cursor=result["next_cursor"],
            has_more=result["has_more"],
        )

    async def get_following(
        self, user_id: str, limit: int | None = None, cursor: str | None = None
    ):
        from app.schemas import FollowingListResponse

        if not limit:
            limit = 20

        result = self.paginate(
            filters={"follower_id": {"op": "==", "value": user_id}},
            order_by="-created_at",
            limit=limit,
            cursor=cursor,
        )

        return FollowingListResponse(
            items=result["items"],
            next_cursor=result["next_cursor"],
            has_more=result["has_more"],
        )
