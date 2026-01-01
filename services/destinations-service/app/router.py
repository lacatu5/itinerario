from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.schemas import (
    AdvertisementCreate,
    AdvertisementResponse,
    AdvertisementsListResponse,
    AdvertisementUpdate,
    DestinationCreate,
    DestinationResponse,
    DestinationsListResponse,
    DestinationUpdate,
    DestinationWithContent,
    DiscountCreate,
    DiscountResponse,
    DiscountsListResponse,
    DiscountUpdate,
    OfferCreate,
    OfferResponse,
    OffersListResponse,
    OfferUpdate,
)
from app.services import (
    AdvertisementService,
    DestinationService,
    DiscountService,
    OfferService,
)
from core.auth.firebase import get_current_user_id

api_router = APIRouter(prefix="/api/destinations", tags=["Destinations"])


def get_ad_service() -> AdvertisementService:
    return AdvertisementService()


def get_discount_service() -> DiscountService:
    return DiscountService()


def get_offer_service() -> OfferService:
    return OfferService()


@api_router.post("/", response_model=DestinationResponse, summary="Create destination")
async def create_destination(
    destination: DestinationCreate,
    user_id: str = Depends(get_current_user_id),
    service: DestinationService = Depends(DestinationService),
):
    return await service.create_destination(destination, user_id)


@api_router.get("/", response_model=DestinationsListResponse, summary="List all destinations")
async def list_destinations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: DestinationService = Depends(DestinationService),
):
    return await service.get_all_destinations(skip=skip, limit=limit)


@api_router.get(
    "/{destination_id}", response_model=DestinationWithContent, summary="Get destination by ID"
)
async def get_destination(
    destination_id: str,
    service: DestinationService = Depends(DestinationService),
):
    return await service.get_destination_with_content(destination_id)


@api_router.put(
    "/{destination_id}", response_model=DestinationResponse, summary="Update destination"
)
async def update_destination(
    destination_id: str,
    destination: DestinationUpdate,
    user_id: str = Depends(get_current_user_id),
    service: DestinationService = Depends(DestinationService),
):
    return await service.update_destination(destination_id, destination, user_id)


@api_router.delete("/{destination_id}", status_code=204, summary="Delete destination")
async def delete_destination(
    destination_id: str,
    user_id: str = Depends(get_current_user_id),
    service: DestinationService = Depends(DestinationService),
) -> None:
    await service.delete_destination(destination_id, user_id)


@api_router.post("/{destination_id}/upload-image", summary="Upload destination image")
async def upload_destination_image(
    destination_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    service: DestinationService = Depends(DestinationService),
):
    return await service.upload_destination_image(destination_id, file, user_id)


@api_router.delete("/{destination_id}/image", status_code=204, summary="Delete destination image")
async def delete_destination_image(
    destination_id: str,
    user_id: str = Depends(get_current_user_id),
    service: DestinationService = Depends(DestinationService),
) -> None:
    await service.delete_destination_image(destination_id, user_id)


@api_router.post(
    "/{destination_id}/advertisements",
    response_model=AdvertisementResponse,
    summary="Create advertisement",
)
async def create_advertisement(
    destination_id: str,
    data: AdvertisementCreate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_ad_service),
):
    return await service.create(destination_id, data, user_id)


@api_router.get(
    "/{destination_id}/advertisements",
    response_model=AdvertisementsListResponse,
    tags=["Advertisements"],
    summary="List advertisements",
)
async def list_advertisements(
    destination_id: str,
    active_only: bool = Query(False),
    service=Depends(get_ad_service),
):
    return await service.list(destination_id, active_only=active_only)


@api_router.put(
    "/{destination_id}/advertisements/{resource_id}",
    response_model=AdvertisementResponse,
    tags=["Advertisements"],
    summary="Update advertisement",
)
async def update_advertisement(
    destination_id: str,
    resource_id: str,
    data: AdvertisementUpdate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_ad_service),
):
    return await service.update(resource_id, data, destination_id, user_id)


@api_router.delete(
    "/{destination_id}/advertisements/{resource_id}",
    tags=["Advertisements"],
    status_code=204,
    summary="Delete advertisement",
)
async def delete_advertisement(
    destination_id: str,
    resource_id: str,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_ad_service),
) -> None:
    await service.delete(resource_id, destination_id, user_id)


@api_router.post(
    "/{destination_id}/discounts", response_model=DiscountResponse, summary="Create discount"
)
async def create_discount(
    destination_id: str,
    data: DiscountCreate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_discount_service),
):
    return await service.create(destination_id, data, user_id)


@api_router.get(
    "/{destination_id}/discounts",
    response_model=DiscountsListResponse,
    tags=["Discounts"],
    summary="List discounts",
)
async def list_discounts(
    destination_id: str,
    active_only: bool = Query(False),
    service=Depends(get_discount_service),
):
    return await service.list(destination_id, active_only=active_only)


@api_router.put(
    "/{destination_id}/discounts/{resource_id}",
    response_model=DiscountResponse,
    tags=["Discounts"],
    summary="Update discount",
)
async def update_discount(
    destination_id: str,
    resource_id: str,
    data: DiscountUpdate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_discount_service),
):
    return await service.update(resource_id, data, destination_id, user_id)


@api_router.delete(
    "/{destination_id}/discounts/{resource_id}",
    tags=["Discounts"],
    status_code=204,
    summary="Delete discount",
)
async def delete_discount(
    destination_id: str,
    resource_id: str,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_discount_service),
) -> None:
    await service.delete(resource_id, destination_id, user_id)


@api_router.post("/{destination_id}/offers", response_model=OfferResponse, summary="Create offer")
async def create_offer(
    destination_id: str,
    data: OfferCreate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_offer_service),
):
    return await service.create(destination_id, data, user_id)


@api_router.get(
    "/{destination_id}/offers",
    response_model=OffersListResponse,
    tags=["Offers"],
    summary="List offers",
)
async def list_offers(
    destination_id: str,
    active_only: bool = Query(False),
    service=Depends(get_offer_service),
):
    return await service.list(destination_id, active_only=active_only)


@api_router.put(
    "/{destination_id}/offers/{resource_id}",
    response_model=OfferResponse,
    tags=["Offers"],
    summary="Update offer",
)
async def update_offer(
    destination_id: str,
    resource_id: str,
    data: OfferUpdate,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_offer_service),
):
    return await service.update(resource_id, data, destination_id, user_id)


@api_router.delete(
    "/{destination_id}/offers/{resource_id}",
    tags=["Offers"],
    status_code=204,
    summary="Delete offer",
)
async def delete_offer(
    destination_id: str,
    resource_id: str,
    user_id: str = Depends(get_current_user_id),
    service=Depends(get_offer_service),
) -> None:
    await service.delete(resource_id, destination_id, user_id)
