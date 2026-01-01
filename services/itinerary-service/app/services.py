from datetime import date, datetime

from fastapi import UploadFile
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Itinerary,
    Location,
    Transport,
)
from app.schemas import (
    ItineraryCreate,
    ItineraryResponse,
    ItinerarySearchResult,
    ItineraryUpdate,
    ItineraryWithOwnerResponse,
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    TransportCreate,
    TransportResponse,
    TransportUpdate,
    UserResponse,
)
from core.auth.ownership import verify_ownership as verify_resource_ownership
from core.exceptions import EntityNotFoundException, ValidationException
from core.identity import UserResolver
from core.storage.images import delete_image, sync_model_image


def strip_timezone_from_dict(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.replace(tzinfo=None)
        else:
            result[key] = value
    return result


class ItineraryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_resolver = UserResolver(db)

    async def create_itinerary(
        self,
        itinerary: ItineraryCreate,
        user_id: str,
    ) -> ItineraryResponse:
        db_user_id = await self.user_resolver.get_user_id(user_id)
        db_itinerary = Itinerary(**itinerary.model_dump(), owner_id=db_user_id)
        self.db.add(db_itinerary)
        await self.db.commit()
        await self.db.refresh(db_itinerary)
        logger.info(
            f"Itinerary created: {itinerary.title} (id: {db_itinerary.id}, owner: {user_id})"
        )
        return ItineraryResponse.model_validate(db_itinerary)

    async def list_itineraries(self, user_id: str | None = None, params: Params | None = None):
        if params is None:
            params = Params()
        if user_id:
            db_user_id = await self.user_resolver.get_user_id(user_id)
            result = await paginate(
                self.db,
                select(Itinerary)
                .filter(Itinerary.owner_id == db_user_id)
                .order_by(Itinerary.created_at.desc()),
                params=params,
            )
        else:
            result = await paginate(
                self.db,
                select(Itinerary).order_by(Itinerary.created_at.desc()),
                params=params,
            )
        result.items = [ItineraryResponse.model_validate(i) for i in result.items]
        logger.info(f"Retrieved {len(result.items)} itineraries")
        return result

    async def get_itinerary_locations(self, itinerary_id: str, params: Params | None = None):
        if params is None:
            params = Params()
        result = await paginate(
            self.db,
            select(Location).filter(Location.itinerary_id == itinerary_id),
            params=params,
        )
        result.items = [LocationResponse.model_validate(location) for location in result.items]
        return result

    async def get_itinerary_transports(self, itinerary_id: str, params: Params | None = None):
        if params is None:
            params = Params()
        result = await paginate(
            self.db,
            select(Transport).filter(Transport.itinerary_id == itinerary_id),
            params=params,
        )
        result.items = [TransportResponse.model_validate(t) for t in result.items]
        return result

    async def update_itinerary(
        self, itinerary_id: int, itinerary_data: ItineraryUpdate, user_id: str
    ) -> ItineraryResponse:
        itinerary = await self.verify_ownership(itinerary_id, user_id)
        update_data = itinerary_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(itinerary, key, value)
        await self.db.commit()
        await self.db.refresh(itinerary)
        logger.info(f"Itinerary {itinerary_id} updated by user {user_id}")
        return ItineraryResponse.model_validate(itinerary)

    async def upload_itinerary_image(
        self, itinerary_id: int, user_id: str, file: UploadFile
    ) -> dict:
        itinerary = await self.verify_ownership(itinerary_id, user_id)
        result = await sync_model_image(
            db=self.db,
            model_instance=itinerary,
            file=file,
            bucket_path="itineraries",
            image_url_field="image_url",
        )
        logger.info(f"Itinerary image uploaded for itinerary {itinerary_id}")
        return result

    async def verify_ownership(self, itinerary_id: int, user_id: str) -> Itinerary:
        db_user_id = await self.user_resolver.get_user_id(user_id)
        itinerary = await self.db.get(Itinerary, itinerary_id)
        if not itinerary:
            raise EntityNotFoundException(f"Itinerary {itinerary_id} not found")
        verify_resource_ownership(itinerary.owner_id, db_user_id, "itinerary")
        logger.debug(f"Ownership verified for itinerary {itinerary_id} by user {user_id}")
        return itinerary

    async def get_itinerary_with_owner_public(
        self, itinerary_id: str
    ) -> ItineraryWithOwnerResponse:
        itinerary = await self.db.get(Itinerary, itinerary_id)
        if not itinerary:
            raise EntityNotFoundException(f"Itinerary {itinerary_id} not found")

        logger.info(f"Retrieved itinerary {itinerary_id} with owner info")
        return ItineraryWithOwnerResponse(
            **ItineraryResponse.model_validate(itinerary).model_dump(),
            owner=UserResponse(
                id=itinerary.owner_id,
                name="",
                username=None,
                profile_image_url=None,
                created_at=itinerary.created_at,
            ),
        )

    async def search_itineraries_with_owners(
        self,
        destination: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search_text: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ItinerarySearchResult:
        query = select(Itinerary)

        if start_date and end_date:
            query = query.where(Itinerary.start_date.between(start_date, end_date))
        elif start_date:
            query = query.where(Itinerary.start_date >= start_date)
        elif end_date:
            query = query.where(Itinerary.end_date <= end_date)

        if destination:
            query = query.where(Itinerary.destination.ilike(f"%{destination}%"))

        if search_text:
            search_query = " ".join(search_text.split())
            query = query.where(
                func.to_tsvector(
                    "english",
                    func.coalesce(Itinerary.title, "")
                    + " "
                    + func.coalesce(Itinerary.short_description, "")
                    + " "
                    + func.coalesce(Itinerary.detail_description, ""),
                ).op("@@")(func.to_tsquery("english", search_query))
            )
            query = query.order_by(
                func.ts_rank(
                    func.to_tsvector(
                        "english",
                        func.coalesce(Itinerary.title, "")
                        + " "
                        + func.coalesce(Itinerary.short_description, "")
                        + " "
                        + func.coalesce(Itinerary.detail_description, ""),
                    ),
                    func.to_tsquery("english", search_query),
                ).desc()
            )
        else:
            query = query.order_by(Itinerary.created_at.desc())

        total_count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.scalar(total_count_query)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        itineraries = result.scalars().all()

        results_with_owners = [
            ItineraryWithOwnerResponse(
                **ItineraryResponse.model_validate(itinerary).model_dump(),
                owner=UserResponse(
                    id=itinerary.owner_id,
                    name="",
                    username=None,
                    profile_image_url=None,
                    created_at=itinerary.created_at,
                ),
            )
            for itinerary in itineraries
        ]

        logger.info(
            f"Searched itineraries - destination: {destination}, start_date: {start_date}, end_date: {end_date}, search_text: {search_text}, results: {len(results_with_owners)}/{total_count}"
        )
        return {"results": results_with_owners, "total": total_count}


class LocationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_resolver = UserResolver(db)

    async def get(self, location_id: str) -> LocationResponse:
        db_location = await self.db.get(Location, location_id)
        if not db_location:
            raise EntityNotFoundException(f"Location {location_id} not found")
        logger.info(f"Retrieved location {location_id}")
        return LocationResponse.model_validate(db_location)

    async def get_by_itinerary(
        self, itinerary_id: int, skip: int = 0, limit: int = 100
    ) -> list[LocationResponse]:
        result = await self.db.execute(
            select(Location)
            .filter(Location.itinerary_id == itinerary_id)
            .order_by(Location.from_date.asc())
            .offset(skip)
            .limit(limit)
        )
        locations = result.scalars().all()
        logger.info(f"Retrieved {len(locations)} locations for itinerary {itinerary_id}")
        return [LocationResponse.model_validate(location) for location in locations]

    async def create(
        self, location: LocationCreate, itinerary_id: int, user_id: str
    ) -> LocationResponse:
        db_user_id = await self.user_resolver.get_user_id(user_id)
        itinerary = await self.db.get(Itinerary, itinerary_id)
        if not itinerary:
            raise EntityNotFoundException(f"Itinerary {itinerary_id} not found")
        verify_resource_ownership(itinerary.owner_id, db_user_id, "location")

        db_location = Location(**location.model_dump(), itinerary_id=itinerary_id)
        self.db.add(db_location)
        await self.db.commit()
        await self.db.refresh(db_location)
        logger.info(
            f"Location created: {location.name} (id: {db_location.id}, itinerary: {itinerary_id})"
        )
        return LocationResponse.model_validate(db_location)

    async def update(
        self, location_id: int, location: LocationUpdate, user_id: str
    ) -> LocationResponse:
        await self.verify_ownership_and_get_itinerary(location_id, user_id)

        db_location = await self.db.get(Location, location_id)
        if not db_location:
            raise EntityNotFoundException(f"Location {location_id} not found")

        update_data = location.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_location, key, value)

        await self.db.commit()
        await self.db.refresh(db_location)
        logger.info(f"Location {location_id} updated by user {user_id}")
        return LocationResponse.model_validate(db_location)

    async def delete(self, location_id: int, user_id: str) -> None:
        await self.verify_ownership_and_get_itinerary(location_id, user_id)

        db_location = await self.db.get(Location, location_id)
        if not db_location:
            raise EntityNotFoundException(f"Location {location_id} not found")

        await self.db.delete(db_location)
        await self.db.commit()
        logger.info(f"Location {location_id} deleted by user {user_id}")

    async def delete_image(self, location_id: int, user_id: str) -> None:
        from core.storage.client import CloudStorageService

        await self.verify_ownership_and_get_itinerary(location_id, user_id)

        db_location = await self.db.get(Location, location_id)
        if not db_location:
            raise EntityNotFoundException(f"Location {location_id} not found")

        if not getattr(db_location, "image_url", None):
            raise ValidationException(f"Location {location_id} has no image")

        cloud_storage = CloudStorageService()
        delete_image(cloud_storage, db_location.image_url, "locations")

        db_location.image_url = None
        await self.db.commit()
        logger.info(f"Location image deleted for location {location_id}")

    async def update_image(self, location_id: int, file: UploadFile, user_id: str) -> dict:
        await self.verify_ownership_and_get_itinerary(location_id, user_id)

        db_location = await self.db.get(Location, location_id)
        if not db_location:
            raise EntityNotFoundException(f"Location {location_id} not found")

        result = await sync_model_image(
            db=self.db,
            model_instance=db_location,
            file=file,
            bucket_path="locations",
            image_url_field="image_url",
        )
        logger.info(f"Location image uploaded for location {location_id}")
        return result

    async def verify_ownership_and_get_itinerary(self, location_id: int, user_id: str) -> Itinerary:
        db_user_id = await self.user_resolver.get_user_id(user_id)
        db_location = await self.db.get(Location, location_id)
        if not db_location:
            raise EntityNotFoundException(f"Location {location_id} not found")

        db_itinerary = await self.db.get(Itinerary, db_location.itinerary_id)
        if not db_itinerary:
            raise EntityNotFoundException(f"Itinerary {db_location.itinerary_id} not found")

        verify_resource_ownership(db_itinerary.owner_id, db_user_id, "location")

        return db_itinerary


class TransportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_resolver = UserResolver(db)

    async def get(self, transport_id: str) -> TransportResponse:
        db_transport = await self.db.get(Transport, transport_id)
        if not db_transport:
            raise EntityNotFoundException(f"Transport {transport_id} not found")
        logger.info(f"Retrieved transport {transport_id}")
        return TransportResponse.model_validate(db_transport)

    async def get_by_itinerary(
        self, itinerary_id: int, skip: int = 0, limit: int = 100
    ) -> list[TransportResponse]:
        result = await self.db.execute(
            select(Transport)
            .filter(Transport.itinerary_id == itinerary_id)
            .order_by(Transport.departure_time.asc())
            .offset(skip)
            .limit(limit)
        )
        transports = result.scalars().all()
        logger.info(f"Retrieved {len(transports)} transports for itinerary {itinerary_id}")
        return [TransportResponse.model_validate(t) for t in transports]

    async def create(
        self, transport: TransportCreate, itinerary_id: int, user_id: str
    ) -> TransportResponse:
        db_user_id = await self.user_resolver.get_user_id(user_id)
        itinerary = await self.db.get(Itinerary, itinerary_id)
        if not itinerary:
            raise EntityNotFoundException(f"Itinerary {itinerary_id} not found")
        verify_resource_ownership(itinerary.owner_id, db_user_id, "transport")

        transport_data = strip_timezone_from_dict(transport.model_dump())
        db_transport = Transport(**transport_data, itinerary_id=itinerary_id)
        self.db.add(db_transport)
        await self.db.commit()
        await self.db.refresh(db_transport)
        logger.info(
            f"Transport created: {transport.type} (id: {db_transport.id}, itinerary: {itinerary_id})"
        )
        return TransportResponse.model_validate(db_transport)

    async def update(
        self, transport_id: int, transport: TransportUpdate, user_id: str
    ) -> TransportResponse:
        await self.verify_ownership_and_get_itinerary(transport_id, user_id)

        db_transport = await self.db.get(Transport, transport_id)
        if not db_transport:
            raise EntityNotFoundException(f"Transport {transport_id} not found")

        update_data = strip_timezone_from_dict(transport.model_dump(exclude_unset=True))
        for key, value in update_data.items():
            setattr(db_transport, key, value)

        await self.db.commit()
        await self.db.refresh(db_transport)
        logger.info(f"Transport {transport_id} updated by user {user_id}")
        return TransportResponse.model_validate(db_transport)

    async def delete(self, transport_id: int, user_id: str) -> None:
        await self.verify_ownership_and_get_itinerary(transport_id, user_id)

        db_transport = await self.db.get(Transport, transport_id)
        if not db_transport:
            raise EntityNotFoundException(f"Transport {transport_id} not found")

        await self.db.delete(db_transport)
        await self.db.commit()
        logger.info(f"Transport {transport_id} deleted by user {user_id}")

    async def verify_ownership_and_get_itinerary(
        self, transport_id: int, user_id: str
    ) -> Itinerary:
        db_user_id = await self.user_resolver.get_user_id(user_id)
        db_transport = await self.db.get(Transport, transport_id)
        if not db_transport:
            raise EntityNotFoundException(f"Transport {transport_id} not found")

        db_itinerary = await self.db.get(Itinerary, db_transport.itinerary_id)
        if not db_itinerary:
            raise EntityNotFoundException(f"Itinerary {db_transport.itinerary_id} not found")

        verify_resource_ownership(db_itinerary.owner_id, db_user_id, "transport")

        return db_itinerary
