from fastapi import UploadFile
from loguru import logger

from app.models import (
    Advertisement,
    Discount,
    Offer,
)
from app.models import (
    Destination as DestinationModel,
)
from app.schemas import (
    AdvertisementCreate,
    AdvertisementsListResponse,
    AdvertisementUpdate,
    DestinationCreate,
    DestinationResponse,
    DestinationsListResponse,
    DestinationUpdate,
    DestinationWithContent,
    DiscountCreate,
    DiscountsListResponse,
    DiscountUpdate,
    OfferCreate,
    OffersListResponse,
    OfferUpdate,
)
from app.schemas import (
    AdvertisementResponse as AdvertisementSchema,
)
from app.schemas import (
    DiscountResponse as DiscountSchema,
)
from app.schemas import (
    OfferResponse as OfferSchema,
)
from core.auth.ownership import verify_ownership
from core.exceptions import EntityNotFoundException
from core.firestore.models import BaseFirestoreService
from core.storage.images import delete_image, upload_image


class AdvertisementService(BaseFirestoreService):
    def __init__(self):
        super().__init__(Advertisement, AdvertisementSchema)

    def verify_ownership(self, destination_id: str, owner_id: str) -> None:
        dest_service = DestinationService()
        dest_service.verify_ownership_for_subresource(destination_id, owner_id)

    async def create(
        self, destination_id: str, data: AdvertisementCreate, owner_id: str | None = None
    ) -> AdvertisementSchema:
        if owner_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Advertisement()
        instance.destination_id = destination_id
        for field, value in data.model_dump().items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Advertisement created for destination {destination_id}")

        return AdvertisementSchema.model_validate(instance)

    async def list(
        self, destination_id: str, active_only: bool = False
    ) -> AdvertisementsListResponse:
        filters = {"destination_id": destination_id}
        if active_only:
            filters["active"] = True
        items = super().list(filters=filters, order_by="-created_at")
        logger.info(f"Retrieved {len(items)} advertisements for destination {destination_id}")
        return AdvertisementsListResponse(items=items, next_cursor=None, has_more=False)

    async def update(
        self,
        resource_id: str,
        data: AdvertisementUpdate,
        destination_id: str | None = None,
        owner_id: str | None = None,
    ) -> AdvertisementSchema | None:
        if owner_id and destination_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Advertisement.collection.get(resource_id)
        if not instance:
            return None
        if destination_id and instance.destination_id != destination_id:
            raise EntityNotFoundException(f"Advertisement {resource_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Advertisement {resource_id} updated")

        return AdvertisementSchema.model_validate(instance)

    async def delete(
        self, resource_id: str, destination_id: str | None = None, owner_id: str | None = None
    ) -> None:
        if owner_id and destination_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Advertisement.collection.get(resource_id)
        if not instance:
            raise EntityNotFoundException(f"Advertisement {resource_id} not found")
        if destination_id and instance.destination_id != destination_id:
            raise EntityNotFoundException(f"Advertisement {resource_id} not found")
        instance.delete()
        logger.info(f"Advertisement {resource_id} deleted")


class DiscountService(BaseFirestoreService):
    def __init__(self):
        super().__init__(Discount, DiscountSchema)

    def verify_ownership(self, destination_id: str, owner_id: str) -> None:
        dest_service = DestinationService()
        dest_service.verify_ownership_for_subresource(destination_id, owner_id)

    async def create(
        self, destination_id: str, data: DiscountCreate, owner_id: str | None = None
    ) -> DiscountSchema:
        if owner_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Discount()
        instance.destination_id = destination_id
        for field, value in data.model_dump().items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Discount created for destination {destination_id}")

        return DiscountSchema.model_validate(instance)

    async def list(self, destination_id: str, active_only: bool = False) -> DiscountsListResponse:
        filters = {"destination_id": destination_id}
        if active_only:
            filters["active"] = True
        items = super().list(filters=filters, order_by="-created_at")
        logger.info(f"Retrieved {len(items)} discounts for destination {destination_id}")
        return DiscountsListResponse(items=items, next_cursor=None, has_more=False)

    async def update(
        self,
        resource_id: str,
        data: DiscountUpdate,
        destination_id: str | None = None,
        owner_id: str | None = None,
    ) -> DiscountSchema | None:
        if owner_id and destination_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Discount.collection.get(resource_id)
        if not instance:
            return None
        if destination_id and instance.destination_id != destination_id:
            raise EntityNotFoundException(f"Discount {resource_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Discount {resource_id} updated")

        return DiscountSchema.model_validate(instance)

    async def delete(
        self, resource_id: str, destination_id: str | None = None, owner_id: str | None = None
    ) -> None:
        if owner_id and destination_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Discount.collection.get(resource_id)
        if not instance:
            raise EntityNotFoundException(f"Discount {resource_id} not found")
        if destination_id and instance.destination_id != destination_id:
            raise EntityNotFoundException(f"Discount {resource_id} not found")
        instance.delete()
        logger.info(f"Discount {resource_id} deleted")


class OfferService(BaseFirestoreService):
    def __init__(self):
        super().__init__(Offer, OfferSchema)

    def verify_ownership(self, destination_id: str, owner_id: str) -> None:
        dest_service = DestinationService()
        dest_service.verify_ownership_for_subresource(destination_id, owner_id)

    async def create(
        self, destination_id: str, data: OfferCreate, owner_id: str | None = None
    ) -> OfferSchema:
        if owner_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Offer()
        instance.destination_id = destination_id
        for field, value in data.model_dump().items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Offer created for destination {destination_id}")

        return OfferSchema.model_validate(instance)

    async def list(self, destination_id: str, active_only: bool = False) -> OffersListResponse:
        filters = {"destination_id": destination_id}
        if active_only:
            filters["active"] = True
        items = super().list(filters=filters, order_by="-created_at")
        logger.info(f"Retrieved {len(items)} offers for destination {destination_id}")
        return OffersListResponse(items=items, next_cursor=None, has_more=False)

    async def update(
        self,
        resource_id: str,
        data: OfferUpdate,
        destination_id: str | None = None,
        owner_id: str | None = None,
    ) -> OfferSchema | None:
        if owner_id and destination_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Offer.collection.get(resource_id)
        if not instance:
            return None
        if destination_id and instance.destination_id != destination_id:
            raise EntityNotFoundException(f"Offer {resource_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Offer {resource_id} updated")

        return OfferSchema.model_validate(instance)

    async def delete(
        self, resource_id: str, destination_id: str | None = None, owner_id: str | None = None
    ) -> None:
        if owner_id and destination_id:
            self.verify_ownership(destination_id, owner_id)

        instance = Offer.collection.get(resource_id)
        if not instance:
            raise EntityNotFoundException(f"Offer {resource_id} not found")
        if destination_id and instance.destination_id != destination_id:
            raise EntityNotFoundException(f"Offer {resource_id} not found")
        instance.delete()
        logger.info(f"Offer {resource_id} deleted")


class DestinationService(BaseFirestoreService):
    def __init__(self):
        super().__init__(DestinationModel, DestinationResponse)

    def _get_verified_destination(self, destination_id: str, owner_id: str) -> DestinationModel:
        destination = DestinationModel.collection.get(destination_id)
        if not destination:
            raise EntityNotFoundException(f"Destination {destination_id} not found")
        verify_ownership(destination.owner_id, owner_id, "destination")
        return destination

    def verify_ownership_for_subresource(self, destination_id: str, owner_id: str) -> None:
        self._get_verified_destination(destination_id, owner_id)

    async def create_destination(
        self, data: DestinationCreate, owner_id: str
    ) -> DestinationResponse:
        instance = DestinationModel()
        instance.owner_id = owner_id
        for field, value in data.model_dump().items():
            setattr(instance, field, value)
        instance.save()
        logger.info(f"Destination created: {instance.name} (id: {instance.id}, owner: {owner_id})")
        return DestinationResponse.model_validate(instance)

    async def get_destinations(self, owner_id: str) -> DestinationsListResponse:
        results = self.list(filters={"owner_id": owner_id}, order_by="-created_at")
        logger.info(f"Retrieved {len(results)} destinations for owner {owner_id}")
        return DestinationsListResponse(items=results, next_cursor=None, has_more=False)

    async def get_all_destinations(
        self, skip: int = 0, limit: int = 50
    ) -> DestinationsListResponse:
        destinations = self.list(order_by="-created_at", limit=limit, skip=skip)
        logger.info(f"Retrieved {len(destinations)} destinations (skip: {skip}, limit: {limit})")
        return DestinationsListResponse(items=destinations, next_cursor=None, has_more=False)

    async def get_destination_with_content(self, destination_id: str) -> DestinationWithContent:
        destination = self.get(destination_id)
        if not destination:
            raise EntityNotFoundException(f"Destination {destination_id} not found")

        ad_service = AdvertisementService()
        offer_service = OfferService()
        discount_service = DiscountService()

        subresources = await self._fetch_subresources(
            destination_id,
            [
                (ad_service, "list", True),
                (offer_service, "list", True),
                (discount_service, "list", True),
            ],
        )

        return DestinationWithContent(
            **destination.model_dump(),
            advertisements=subresources[0].items,
            offers=subresources[1].items,
            discounts=subresources[2].items,
        )

    async def _fetch_subresources(self, destination_id: str, service_calls: list) -> list:
        results = []
        for service, method_name, active_only in service_calls:
            method = getattr(service, method_name)
            result = await method(destination_id, active_only=active_only)
            results.append(result)
        return results

    async def update_destination(
        self, destination_id: str, data: DestinationUpdate, owner_id: str
    ) -> DestinationResponse:
        self._get_verified_destination(destination_id, owner_id)
        result = self.update(destination_id, data)
        if not result:
            raise EntityNotFoundException(f"Destination {destination_id} not found")
        logger.info(f"Destination {destination_id} updated by owner {owner_id}")
        return result

    async def delete_destination(self, destination_id: str, owner_id: str) -> None:
        destination = self._get_verified_destination(destination_id, owner_id)
        destination.delete()
        logger.info(f"Destination {destination_id} deleted")

    async def upload_destination_image(
        self, destination_id: str, file: UploadFile, owner_id: str
    ) -> dict:
        destination = self._get_verified_destination(destination_id, owner_id)
        image_url = upload_image(file, "destinations", destination_id, destination.image_url)
        result = self.update(destination_id, DestinationUpdate(image_url=image_url))
        logger.info(f"Destination image uploaded for {destination_id}")
        return {"message": "Destination image uploaded successfully", "destination": result}

    async def delete_destination_image(self, destination_id: str, owner_id: str) -> None:
        destination = self._get_verified_destination(destination_id, owner_id)
        delete_image(destination.image_url)
        self.update(destination_id, DestinationUpdate(image_url=None))
        logger.info(f"Destination image deleted for {destination_id}")
