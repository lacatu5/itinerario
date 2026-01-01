from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    PublicUserResponse,
    SearchUsersResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services import UserService
from core.auth.firebase import get_current_user_id
from core.database.connection import get_db


def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


api_router = APIRouter(prefix="/api/users", tags=["Users"])


@api_router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create user"
)
async def create_user(user: UserCreate, user_service=Depends(get_user_service)):
    return await user_service.create_user(user)


@api_router.get(
    "/internal/firebase/{firebase_uid}",
    response_model=UserResponse,
    summary="Get user by Firebase UID (internal, no auth)",
)
async def get_user_by_firebase_uid_internal(
    firebase_uid: str,
    user_service=Depends(get_user_service),
):
    return await user_service.get_user_by_firebase_uid_no_auth(firebase_uid)


@api_router.get("/", response_model=Page[UserResponse], summary="List all users")
async def list_users(params: Params = Depends(), user_service=Depends(get_user_service)):
    return await user_service.get_users_paginated(params)


@api_router.get("/search", response_model=SearchUsersResponse, summary="Search users")
async def search_users(
    query: str = Query(..., min_length=1), user_service=Depends(get_user_service)
):
    return await user_service.search_users(query)


@api_router.get("/email/{email}", response_model=UserResponse, summary="Get user by email")
async def get_user_by_email(
    email: str,
    user_service=Depends(get_user_service),
    current_user_id: str = Depends(get_current_user_id),
):
    return await user_service.get_user_by_email(email, current_user_id)


@api_router.get("/{firebase_uid}", response_model=UserResponse, summary="Get user by Firebase UID")
async def get_user(
    firebase_uid: str,
    user_service=Depends(get_user_service),
    current_user_id: str = Depends(get_current_user_id),
):
    return await user_service.get_user_by_id(firebase_uid, current_user_id)


@api_router.get(
    "/{firebase_uid}/public",
    response_model=PublicUserResponse,
    summary="Get public user profile",
)
async def get_public_user(
    firebase_uid: str,
    user_service=Depends(get_user_service),
    current_user_id: str = Depends(get_current_user_id),
):
    return await user_service.get_public_user(firebase_uid)


@api_router.put("/{firebase_uid}", response_model=UserResponse, summary="Update user")
async def update_user(
    firebase_uid: str,
    user_update: UserUpdate,
    user_service=Depends(get_user_service),
    current_user_id: str = Depends(get_current_user_id),
):
    return await user_service.update_user(firebase_uid, user_update, current_user_id)


@api_router.post("/{firebase_uid}/upload-image", summary="Upload user image")
async def upload_user_image(
    firebase_uid: str,
    file: UploadFile = File(...),
    user_service=Depends(get_user_service),
    current_user_id: str = Depends(get_current_user_id),
) -> dict:
    return await user_service.upload_user_image(firebase_uid, file, current_user_id)


@api_router.delete("/{firebase_uid}/image", status_code=204, summary="Delete user image")
async def delete_user_image(
    firebase_uid: str,
    user_service=Depends(get_user_service),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    await user_service.delete_user_image(firebase_uid, current_user_id)
