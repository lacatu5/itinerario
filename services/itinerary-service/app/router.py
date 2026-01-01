from fastapi import (
    APIRouter,
    Depends,
    File,
    Query,
    UploadFile,
)
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.firebase import get_current_user_id
from app.schemas import (
    ItineraryCreate,
    ItineraryResponse,
    ItinerarySearchRequest,
    ItinerarySearchResult,
    ItineraryUpdate,
    ItineraryWithOwnerResponse,
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    TransportCreate,
    TransportResponse,
    TransportUpdate,
)
from app.services import ItineraryService, LocationService, TransportService
from core.database.connection import get_db


async def get_itinerary_service(db: AsyncSession = Depends(get_db)):
    return ItineraryService(db)


async def get_location_service(db: AsyncSession = Depends(get_db)):
    return LocationService(db)


async def get_transport_service(db: AsyncSession = Depends(get_db)):
    return TransportService(db)


api_router = APIRouter(prefix="/api/itineraries", tags=["Itineraries"])


@api_router.post("/", response_model=ItineraryResponse, summary="Create itinerary")
async def create_itinerary(
    itinerary: ItineraryCreate,
    user_id: str = Depends(get_current_user_id),
    itinerary_service=Depends(get_itinerary_service),
):
    return await itinerary_service.create_itinerary(itinerary, user_id)


@api_router.get(
    "/user/{user_id}", response_model=Page[ItineraryResponse], summary="Get itineraries by user"
)
async def get_itineraries_by_user(
    user_id: str, params: Params = Depends(), itinerary_service=Depends(get_itinerary_service)
):
    return await itinerary_service.list_itineraries(user_id, params)


@api_router.get("/", response_model=Page[ItineraryResponse], summary="List all itineraries")
async def list_itineraries(
    user_id: str | None = Query(None, description="Filter by user ID"),
    params: Params = Depends(),
    itinerary_service=Depends(get_itinerary_service),
):
    return await itinerary_service.list_itineraries(user_id, params)


@api_router.post("/search", response_model=ItinerarySearchResult, summary="Search itineraries")
async def search_itineraries(
    search_request: ItinerarySearchRequest,
    itinerary_service=Depends(get_itinerary_service),
):
    return await itinerary_service.search_itineraries_with_owners(**search_request.model_dump())


@api_router.get(
    "/{itinerary_id}", response_model=ItineraryWithOwnerResponse, summary="Get itinerary by ID"
)
async def get_itinerary(itinerary_id: int, itinerary_service=Depends(get_itinerary_service)):
    return await itinerary_service.get_itinerary_with_owner_public(itinerary_id)


@api_router.put("/{itinerary_id}", response_model=ItineraryResponse, summary="Update itinerary")
async def update_itinerary(
    itinerary_id: int,
    itinerary: ItineraryUpdate,
    user_id: str = Depends(get_current_user_id),
    itinerary_service=Depends(get_itinerary_service),
):
    return await itinerary_service.update_itinerary(itinerary_id, itinerary, user_id)


@api_router.post(
    "/{itinerary_id}/locations",
    response_model=LocationResponse,
    summary="Create location for itinerary",
)
async def create_location_for_itinerary(
    itinerary_id: int,
    location: LocationCreate,
    user_id: str = Depends(get_current_user_id),
    location_service=Depends(get_location_service),
):
    return await location_service.create(location, itinerary_id, user_id)


@api_router.get(
    "/{itinerary_id}/locations",
    response_model=Page[LocationResponse],
    summary="Get itinerary locations",
)
async def get_itinerary_locations(
    itinerary_id: int, params: Params = Depends(), itinerary_service=Depends(get_itinerary_service)
):
    return await itinerary_service.get_itinerary_locations(itinerary_id, params)


@api_router.post(
    "/{itinerary_id}/transports",
    response_model=TransportResponse,
    summary="Create transport for itinerary",
)
async def create_transport_for_itinerary(
    itinerary_id: int,
    transport: TransportCreate,
    user_id: str = Depends(get_current_user_id),
    transport_service=Depends(get_transport_service),
):
    return await transport_service.create(transport, itinerary_id, user_id)


@api_router.get(
    "/{itinerary_id}/transports",
    response_model=Page[TransportResponse],
    summary="Get itinerary transports",
)
async def get_itinerary_transports(
    itinerary_id: int, params: Params = Depends(), itinerary_service=Depends(get_itinerary_service)
):
    return await itinerary_service.get_itinerary_transports(itinerary_id, params)


@api_router.post("/{itinerary_id}/upload-image", summary="Upload itinerary image")
async def upload_itinerary_image(
    itinerary_id: int,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    itinerary_service=Depends(get_itinerary_service),
):
    return await itinerary_service.upload_itinerary_image(itinerary_id, user_id, file)


@api_router.put(
    "/locations/{location_id}", response_model=LocationResponse, summary="Update location"
)
async def update_location(
    location_id: int,
    location: LocationUpdate,
    user_id: str = Depends(get_current_user_id),
    location_service=Depends(get_location_service),
):
    return await location_service.update(location_id, location, user_id)


@api_router.delete("/locations/{location_id}", status_code=204, summary="Delete location")
async def delete_location(
    location_id: int,
    user_id: str = Depends(get_current_user_id),
    location_service=Depends(get_location_service),
) -> None:
    await location_service.delete(location_id, user_id)


@api_router.delete(
    "/locations/{location_id}/image", status_code=204, summary="Delete location image"
)
async def delete_location_image(
    location_id: int,
    user_id: str = Depends(get_current_user_id),
    location_service=Depends(get_location_service),
) -> None:
    await location_service.delete_image(location_id, user_id)


@api_router.post("/locations/{location_id}/upload-image", summary="Upload location image")
async def upload_location_image(
    location_id: int,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    location_service=Depends(get_location_service),
):
    return await location_service.update_image(location_id, file, user_id)


@api_router.put(
    "/transports/{transport_id}", response_model=TransportResponse, summary="Update transport"
)
async def update_transport(
    transport_id: int,
    transport: TransportUpdate,
    user_id: str = Depends(get_current_user_id),
    transport_service=Depends(get_transport_service),
):
    return await transport_service.update(transport_id, transport, user_id)


@api_router.delete("/transports/{transport_id}", status_code=204, summary="Delete transport")
async def delete_transport(
    transport_id: int,
    user_id: str = Depends(get_current_user_id),
    transport_service=Depends(get_transport_service),
) -> None:
    await transport_service.delete(transport_id, user_id)
