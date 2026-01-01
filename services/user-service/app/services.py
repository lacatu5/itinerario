import random
import string

from fastapi import UploadFile
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import SearchUsersResponse, UserCreate, UserResponse, UserUpdate
from core.auth.ownership import verify_ownership as verify_resource_ownership
from core.exceptions import (
    EntityNotFoundException,
    ValidationException,
)
from core.storage.images import sync_model_image
from core.storage.client import CloudStorageService


def generate_username_from_email(email: str) -> str:
    base = email.split("@")[0].lower()
    base = "".join(ch for ch in base if ch.isalnum())
    base = base[:20]

    alphabet = string.ascii_lowercase + string.digits
    suffix = "".join(random.choice(alphabet) for _ in range(3))

    return f"{base}{suffix}"


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_firebase_user(self, firebase_uid: str, user_info: dict) -> UserResponse:
        email = user_info.get("email")
        name = user_info.get("name")

        if not email:
            raise ValidationException("Email is required from Firebase token")

        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            logger.info(f"Existing Firebase user retrieved: {email}")
            return UserResponse.model_validate(db_user)

        user_create = UserCreate(
            firebase_uid=firebase_uid, name=name or email.split("@")[0], email=email
        )
        logger.info(f"Creating new Firebase user: {email}")
        return await self.create_user(user_create)

    async def get_users_paginated(self, params: Params | None = None) -> Page[UserResponse]:
        if params is None:
            params = Params()
        result = await paginate(
            self.db,
            select(User).order_by(User.id),
            params=params,
        )
        result.items = [UserResponse.model_validate(u) for u in result.items]
        logger.info(f"Retrieved {len(result.items)} users")
        return result

    async def get_user_by_id(self, user_id: str, current_user_id: str) -> UserResponse:
        verify_resource_ownership(user_id, current_user_id, "user")

        stmt = select(User).where(User.firebase_uid == user_id)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise EntityNotFoundException(f"User {user_id} not found")
        return UserResponse.model_validate(db_user)

    async def get_user_by_email(self, email: str, current_user_id: str) -> UserResponse:
        stmt = select(User).where(User.email.ilike(email))
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise EntityNotFoundException(f"User with email {email} not found")

        verify_resource_ownership(db_user.firebase_uid, current_user_id, "user")
        return UserResponse.model_validate(db_user)

    async def get_user_by_firebase_uid(
        self, firebase_uid: str, current_user_id: str
    ) -> UserResponse:
        verify_resource_ownership(firebase_uid, current_user_id, "user")

        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise EntityNotFoundException(f"User with Firebase UID {firebase_uid} not found")
        return UserResponse.model_validate(db_user)

    async def update_user(
        self, user_id: str, user_update: UserUpdate, current_user_id: str
    ) -> UserResponse:
        verify_resource_ownership(user_id, current_user_id, "user")

        stmt = select(User).where(User.firebase_uid == user_id)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise EntityNotFoundException(f"User {user_id} not found")

        if user_update.username is not None:
            existing_stmt = select(User).where(User.username == user_update.username)
            existing_result = await self.db.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()
            if existing and existing.firebase_uid != user_id:
                raise ValidationException("Username already taken")

        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)

        await self.db.commit()
        await self.db.refresh(db_user)

        return UserResponse.model_validate(db_user)

    async def upload_user_image(self, user_id: str, file: UploadFile, current_user_id: str) -> dict:
        logger.info(f"Upload request received for firebase_uid: {user_id}")
        logger.info(
            f"File type: {type(file)}, filename: {file.filename}, content_type: {file.content_type}"
        )
        verify_resource_ownership(user_id, current_user_id, "user profile")

        stmt = select(User).where(User.firebase_uid == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return await sync_model_image(
            db=self.db,
            model_instance=user,
            file=file,
            bucket_path="profiles",
            image_url_field="profile_image_url",
            max_size=5 * 1024 * 1024,
        )

    async def delete_user_image(self, user_id: str, current_user_id: str) -> None:
        verify_resource_ownership(user_id, current_user_id, "user profile")

        stmt = select(User).where(User.firebase_uid == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            current_profile_image_url = getattr(user, "profile_image_url", None)
            if current_profile_image_url:
                cloud_storage = CloudStorageService()
                cloud_storage.delete_image(current_profile_image_url)

            user.profile_image_url = None
            await self.db.commit()

    async def get_public_user(self, firebase_uid: str):
        from app.schemas import PublicUserResponse

        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise EntityNotFoundException(f"User {firebase_uid} not found")
        return PublicUserResponse.model_validate(db_user)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        stmt = select(User).where(User.email.ilike(user_data.email))
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValidationException("User with this email already exists")

        username = user_data.username or generate_username_from_email(user_data.email)
        if await self.username_exists(username):
            raise ValidationException("Username already taken")

        new_user = User(
            firebase_uid=user_data.firebase_uid,
            name=user_data.name,
            email=user_data.email,
            username=username,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        logger.info(f"User created successfully: {new_user.email} (username: {new_user.username})")
        return UserResponse.model_validate(new_user)

    async def username_exists(self, username: str, exclude_user_id: str | None = None) -> bool:
        stmt = select(User).where(User.username == username)
        if exclude_user_id:
            stmt = stmt.where(User.firebase_uid != exclude_user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def search_users(self, query: str) -> SearchUsersResponse:
        lower_query = query.lower()
        result = await self.db.execute(
            select(User)
            .where(
                (User.name.ilike(f"%{lower_query}%")) | (User.username.ilike(f"%{lower_query}%"))
            )
            .limit(20)
        )
        users = result.scalars().all()

        users_public = [UserResponse.model_validate(u) for u in users]
        total_count = len(users_public)
        logger.info(f"User search completed: query='{query}', results={total_count}")
        return SearchUsersResponse(users=users_public, total_count=total_count)
