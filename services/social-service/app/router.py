from fastapi import APIRouter, Body, Depends, Query, Request

from app.schemas import (
    FollowersListResponse,
    FollowCreate,
    FollowingListResponse,
    FollowResponse,
    ItineraryStats,
    LikeCreate,
    LikeResponse,
    LikesListResponse,
    LikeStatusResponse,
    LikeUpdate,
)
from app.services import FollowService, LikeService
from core.auth.firebase import get_current_user_id
from core.config import centrifugo_settings
from core.messaging.client import CentrifugoClient
from core.messaging.utils import generate_centrifugo_token


def get_centrifugo_client(request: Request) -> CentrifugoClient:
    return request.app.state.centrifugo_client


def get_like_service(
    centrifugo_client: CentrifugoClient = Depends(get_centrifugo_client),
) -> LikeService:
    return LikeService(centrifugo_client)


def get_follow_service(
    centrifugo_client: CentrifugoClient = Depends(get_centrifugo_client),
) -> FollowService:
    return FollowService(centrifugo_client)


api_router = APIRouter(prefix="/api/social", tags=["Social"])


@api_router.post(
    "/itineraries/{itinerary_id}/like", response_model=LikeResponse, summary="Like an itinerary"
)
async def like_itinerary(
    itinerary_id: str,
    like_data: LikeCreate = Body(...),
    user_id: str = Depends(get_current_user_id),
    like_service: LikeService = Depends(get_like_service),
):
    like = await like_service.add_like(itinerary_id, user_id, like_data.comment)
    await like_service.publish_new_like(itinerary_id, user_id, like)
    return like


@api_router.delete(
    "/itineraries/{itinerary_id}/like", status_code=204, summary="Unlike an itinerary"
)
async def unlike_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user_id),
    like_service: LikeService = Depends(get_like_service),
) -> None:
    await like_service.remove_like(itinerary_id, user_id)


@api_router.put(
    "/itineraries/{itinerary_id}/like", response_model=LikeResponse, summary="Update like comment"
)
async def update_like_comment(
    itinerary_id: str,
    like_update: LikeUpdate = Body(...),
    user_id: str = Depends(get_current_user_id),
    like_service: LikeService = Depends(get_like_service),
):
    updated_like = await like_service.update_like_comment(
        itinerary_id, user_id, like_update.comment
    )
    return updated_like


@api_router.get(
    "/itineraries/{itinerary_id}/likes",
    response_model=LikesListResponse,
    summary="Get itinerary likes",
)
async def get_itinerary_likes(
    itinerary_id: str,
    limit: int | None = Query(None, ge=1, le=100),
    cursor: str | None = Query(None),
    user_id: str = Depends(get_current_user_id),
    like_service: LikeService = Depends(get_like_service),
):
    return await like_service.get_likes_for_itinerary(itinerary_id, limit, cursor)


@api_router.get(
    "/itineraries/{itinerary_id}/stats",
    response_model=ItineraryStats,
    summary="Get itinerary statistics",
)
async def get_itinerary_stats(
    itinerary_id: str,
    user_id: str = Depends(get_current_user_id),
    like_service: LikeService = Depends(get_like_service),
):
    return await like_service.get_itinerary_stats(itinerary_id)


@api_router.get(
    "/itineraries/{itinerary_id}/like-status",
    response_model=LikeStatusResponse,
    summary="Check like status",
)
async def check_like_status(
    itinerary_id: str,
    user_id: str = Depends(get_current_user_id),
    like_service: LikeService = Depends(get_like_service),
):
    return await like_service.get_like_status(itinerary_id, user_id)


@api_router.post("/follow", response_model=FollowResponse, summary="Follow a user")
async def follow(
    follow_request: FollowCreate = Body(...),
    user_id: str = Depends(get_current_user_id),
    follow_service: FollowService = Depends(get_follow_service),
):
    follow = await follow_service.follow_user(
        follow_request.follower_id, follow_request.following_id
    )
    await follow_service.publish_new_follower(
        follow_request.follower_id, follow_request.following_id
    )
    return follow


@api_router.get(
    "/followers/{user_id}", response_model=FollowersListResponse, summary="Get user followers"
)
async def followers(
    user_id: str,
    limit: int | None = Query(None, ge=1, le=100),
    cursor: str | None = Query(None),
    current_user_id: str = Depends(get_current_user_id),
    follow_service: FollowService = Depends(get_follow_service),
):
    return await follow_service.get_followers(user_id, limit, cursor)


@api_router.get(
    "/following/{user_id}", response_model=FollowingListResponse, summary="Get user following"
)
async def following(
    user_id: str,
    limit: int | None = Query(None, ge=1, le=100),
    cursor: str | None = Query(None),
    current_user_id: str = Depends(get_current_user_id),
    follow_service: FollowService = Depends(get_follow_service),
):
    return await follow_service.get_following(user_id, limit, cursor)


@api_router.post("/centrifugo-token", summary="Get Centrifugo WebSocket token")
async def get_centrifugo_token(
    user_id: str = Depends(get_current_user_id),
):
    token = generate_centrifugo_token(user_id, centrifugo_settings.CENTRIFUGO_HMAC_SECRET_KEY)
    return {
        "token": token,
        "ws_url": centrifugo_settings.CENTRIFUGO_WS_URL,
        "user_id": user_id,
    }
