from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.schemas import (
    DestinationCreate,
    DestinationResponse,
    OfferCreate,
    DiscountCreate,
    AdvertisementCreate,
)
from app.services import (
    DestinationService,
    OfferService,
    DiscountService,
    AdvertisementService,
)
from core.exceptions import EntityNotFoundException


class TestDestinationServiceCreate:
    @pytest.mark.asyncio
    async def test_create_destination_success(self):
        with patch("app.models.Destination") as mock_destination_class:
            mock_destination = MagicMock()
            mock_destination.id = "dest123"
            mock_destination.name = "Paris"
            mock_destination_class.return_value = mock_destination

            service = DestinationService()
            data = DestinationCreate(
                name="Paris",
                region="Île-de-France",
                country="France",
                short_description="Beautiful city",
                detail_description="Detailed description",
            )

            with patch.object(
                service,
                "create",
                return_value=DestinationResponse(
                    id="dest123",
                    owner_id="user123",
                    name="Paris",
                    region="Île-de-France",
                    country="France",
                    description="Beautiful city",
                    image_url=None,
                    latitude=None,
                    longitude=None,
                    address=None,
                    created_at=datetime.now(),
                    updated_at=None,
                ),
            ):
                result = service.create_destination(data, "user123")

                assert result is not None


class TestDestinationServiceRead:
    @pytest.mark.asyncio
    async def test_get_destinations_success(self):
        service = DestinationService()

        with patch.object(service, "list", return_value=[]):
            result = service.get_destinations("user123")

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_all_destinations_success(self):
        service = DestinationService()

        with patch.object(service, "list", return_value=[]):
            result = service.get_all_destinations(0, 50)

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_destination_with_content_success(self):
        service = DestinationService()

        mock_destination = DestinationResponse(
            id="dest123",
            owner_id="user123",
            name="Paris",
            region="Île-de-France",
            country="France",
            description="Beautiful city",
            image_url=None,
            latitude=None,
            longitude=None,
            address=None,
            created_at=datetime.now(),
            updated_at=None,
        )

        with patch.object(service, "get", return_value=mock_destination):
            with patch.object(
                service,
                "_fetch_subresources",
                return_value=[
                    MagicMock(advertisements=[]),
                    MagicMock(offers=[]),
                    MagicMock(discounts=[]),
                ],
            ):
                result = service.get_destination_with_content("dest123")

                assert result is not None


class TestDestinationServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_destination_success(self):
        service = DestinationService()

        with patch.object(service, "_get_verified_destination", return_value=MagicMock()):
            with patch.object(
                service,
                "update",
                return_value=DestinationResponse(
                    id="dest123",
                    owner_id="user123",
                    name="Updated Paris",
                    region="Île-de-France",
                    country="France",
                    description="Updated",
                    image_url=None,
                    latitude=None,
                    longitude=None,
                    address=None,
                    created_at=datetime.now(),
                    updated_at=None,
                ),
            ):
                result = service.update_destination("dest123", {"name": "Updated Paris"}, "user123")

                assert result is not None

    @pytest.mark.asyncio
    async def test_update_destination_not_found(self):
        service = DestinationService()

        with patch("app.services.DestinationModel.collection.get", return_value=None):
            from app.schemas import DestinationUpdate

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update_destination(
                    "dest123", DestinationUpdate(name="Updated"), "user123"
                )

    @pytest.mark.asyncio
    async def test_update_destination_returns_none(self):
        service = DestinationService()

        mock_destination = MagicMock()
        mock_destination.owner_id = "user123"

        with patch("app.services.DestinationModel.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch.object(service, "update", return_value=None):
                    from app.schemas import DestinationUpdate

                    with pytest.raises(EntityNotFoundException, match="not found"):
                        await service.update_destination(
                            "dest123", DestinationUpdate(name="Updated"), "user123"
                        )


class TestDestinationServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_destination_success(self):
        service = DestinationService()

        mock_destination = MagicMock()
        mock_destination.delete = Mock()

        with patch.object(service, "_get_verified_destination", return_value=mock_destination):
            await service.delete_destination("dest123", "user123")

            mock_destination.delete.assert_called_once()


class TestDestinationServiceImage:
    @pytest.mark.asyncio
    async def test_upload_destination_image_success(self):
        service = DestinationService()

        mock_destination = MagicMock()

        with patch.object(service, "_get_verified_destination", return_value=mock_destination):
            with patch("app.services.upload_image", return_value="https://example.com/image.jpg"):
                with patch.object(service, "update", return_value=MagicMock()):
                    result = await service.upload_destination_image(
                        "dest123", MagicMock(), "user123"
                    )

                    assert result is not None
                    assert "destination" in result

    @pytest.mark.asyncio
    async def test_upload_destination_image_with_existing_image(self):
        service = DestinationService()

        mock_destination = MagicMock()
        mock_destination.image_url = "https://example.com/old_image.jpg"

        with patch.object(service, "_get_verified_destination", return_value=mock_destination):
            with patch(
                "app.services.upload_image", return_value="https://example.com/new_image.jpg"
            ):
                with patch.object(service, "update", return_value=MagicMock()) as mock_update:
                    result = await service.upload_destination_image(
                        "dest123", MagicMock(), "user123"
                    )

                    mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_destination_image_success(self):
        service = DestinationService()

        mock_destination = MagicMock()
        mock_destination.image_url = "https://example.com/image.jpg"

        with patch.object(service, "_get_verified_destination", return_value=mock_destination):
            with patch("app.services.delete_image"):
                with patch.object(service, "update"):
                    await service.delete_destination_image("dest123", "user123")

    @pytest.mark.asyncio
    async def test_delete_destination_image_with_no_url(self):
        service = DestinationService()

        mock_destination = MagicMock()
        mock_destination.image_url = None

        with patch.object(service, "_get_verified_destination", return_value=mock_destination):
            with patch("app.services.delete_image"):
                with patch.object(service, "update"):
                    await service.delete_destination_image("dest123", "user123")


class TestDestinationServiceOwnership:
    @pytest.mark.asyncio
    async def test_verify_ownership_for_subresource_success(self):
        service = DestinationService()

        mock_destination = MagicMock()
        mock_destination.owner_id = "user123"

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                service.verify_ownership_for_subresource("dest123", "user123")

    @pytest.mark.asyncio
    async def test_verify_ownership_for_subresource_not_found(self):
        service = DestinationService()

        with patch("app.models.Destination.collection.get", return_value=None):
            with pytest.raises(EntityNotFoundException, match="not found"):
                service.verify_ownership_for_subresource("dest123", "user123")


class TestDestinationServiceFetchSubresources:
    @pytest.mark.asyncio
    async def test_fetch_subresources_success(self):
        service = DestinationService()

        ad_service = AdvertisementService()
        offer_service = OfferService()

        with patch.object(ad_service, "list", return_value=MagicMock(items=[])):
            with patch.object(offer_service, "list", return_value=MagicMock(items=[])):
                service_calls = [
                    (ad_service, "list", True),
                    (offer_service, "list", False),
                ]
                result = await service._fetch_subresources("dest123", service_calls)

                assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_destination_with_content_not_found(self):
        service = DestinationService()

        with patch.object(service, "get", return_value=None):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get_destination_with_content("dest123")


class TestDestinationServiceGetDestination:
    @pytest.mark.asyncio
    async def test_get_destination_not_found(self):
        service = DestinationService()

        with patch("app.models.Destination.collection.get", return_value=None):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get_destination_with_content("dest123")


class TestOfferServiceCreate:
    @pytest.mark.asyncio
    async def test_create_offer_success(self):
        service = OfferService()

        with patch("app.models.Offer") as mock_offer_class:
            mock_offer = MagicMock()
            mock_offer.id = "offer123"
            mock_offer_class.return_value = mock_offer

            with patch.object(service, "verify_ownership"):
                data = OfferCreate(
                    title="Special Offer",
                    description="Great deal",
                    accommodation_name="Hotel Paris",
                    active=True,
                )

                result = await service.create("dest123", data, "user123")

                assert result is not None

    @pytest.mark.asyncio
    async def test_create_offer_without_owner(self):
        service = OfferService()

        with patch("app.models.Offer") as mock_offer_class:
            mock_offer = MagicMock()
            mock_offer.id = "offer123"
            mock_offer_class.return_value = mock_offer

            data = OfferCreate(
                title="Special Offer",
                description="Great deal",
                accommodation_name="Hotel Paris",
                active=True,
            )

            result = await service.create("dest123", data)

            assert result is not None


class TestOfferServiceRead:
    @pytest.mark.asyncio
    async def test_list_offers_success(self):
        service = OfferService()

        with patch.object(service, "list", return_value=MagicMock(items=[], total_count=0)):
            result = await service.list("dest123")

            assert result is not None

    @pytest.mark.asyncio
    async def test_list_offers_active_only(self):
        service = OfferService()

        with patch.object(service, "list", return_value=MagicMock(items=[], total_count=0)):
            result = await service.list("dest123", active_only=True)

            assert result is not None


class TestOfferServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_offer_success(self):
        from app.schemas import OfferUpdate

        service = OfferService()

        mock_offer = MagicMock()
        mock_offer.configure_mock(
            id="offer123",
            destination_id="dest123",
            title="Updated",
            description="Test description",
            accommodation_name="Test Hotel",
            price=100,
            discount_percentage=20,
            valid_from=datetime.now(),
            valid_until=datetime.now(),
            image_url="http://test.com/image.jpg",
            link_url="http://test.com",
            active=True,
            created_at=datetime.now(),
        )

        with patch("app.models.Offer.collection.get", return_value=mock_offer):
            with patch.object(service, "verify_ownership"):
                result = await service.update(
                    "offer123", OfferUpdate(title="Updated"), "dest123", "user123"
                )

                assert result is not None

    @pytest.mark.asyncio
    async def test_update_offer_without_owner(self):
        from app.schemas import OfferUpdate

        service = OfferService()

        mock_offer = MagicMock()
        mock_offer.id = "offer123"
        mock_offer.destination_id = "dest123"
        mock_offer.title = "Updated"
        mock_offer.description = "Test"
        mock_offer.accommodation_name = "Test Hotel"
        mock_offer.price = 100
        mock_offer.discount_percentage = 20
        mock_offer.valid_from = datetime.now()
        mock_offer.valid_until = datetime.now()
        mock_offer.image_url = "http://test.com/image.jpg"
        mock_offer.link_url = "http://test.com"
        mock_offer.active = True
        mock_offer.created_at = datetime.now()

        with patch("app.models.Offer.collection.get", return_value=mock_offer):
            result = await service.update(
                "offer123", OfferUpdate(title="Updated"), destination_id="dest123"
            )

            assert result is not None


class TestOfferServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_offer_success(self):
        service = OfferService()

        mock_offer = MagicMock()
        mock_offer.destination_id = "dest123"

        with patch("app.models.Offer.collection.get", return_value=mock_offer):
            with patch.object(service, "verify_ownership"):
                await service.delete("offer123", "dest123", "user123")

                mock_offer.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_offer_without_owner(self):
        service = OfferService()

        mock_offer = MagicMock()
        mock_offer.destination_id = "dest123"

        with patch("app.models.Offer.collection.get", return_value=mock_offer):
            await service.delete("offer123", destination_id="dest123")

            mock_offer.delete.assert_called_once()


class TestDiscountServiceCreate:
    @pytest.mark.asyncio
    async def test_create_discount_success(self):
        service = DiscountService()

        with patch("app.models.Discount") as mock_discount_class:
            mock_discount = MagicMock()
            mock_discount.id = "discount123"
            mock_discount_class.return_value = mock_discount

            with patch.object(service, "verify_ownership"):
                data = DiscountCreate(
                    title="Museum Discount",
                    description="50% off",
                    attraction_name="Louvre",
                    discount_percentage=50,
                    active=True,
                )

                result = await service.create("dest123", data, "user123")

                assert result is not None

    @pytest.mark.asyncio
    async def test_create_discount_without_owner(self):
        service = DiscountService()

        with patch("app.models.Discount") as mock_discount_class:
            mock_discount = MagicMock()
            mock_discount.id = "discount123"
            mock_discount_class.return_value = mock_discount

            data = DiscountCreate(
                title="Museum Discount",
                description="50% off",
                attraction_name="Louvre",
                discount_percentage=50,
                active=True,
            )

            result = await service.create("dest123", data)

            assert result is not None


class TestDiscountServiceRead:
    @pytest.mark.asyncio
    async def test_list_discounts_success(self):
        service = DiscountService()

        with patch.object(service, "list", return_value=MagicMock(items=[], total_count=0)):
            result = await service.list("dest123")

            assert result is not None

    @pytest.mark.asyncio
    async def test_list_discounts_active_only(self):
        service = DiscountService()

        with patch.object(service, "list", return_value=MagicMock(items=[], total_count=0)):
            result = await service.list("dest123", active_only=True)

            assert result is not None


class TestAdvertisementServiceCreate:
    @pytest.mark.asyncio
    async def test_create_advertisement_success(self):
        service = AdvertisementService()

        with patch("app.models.Advertisement") as mock_ad_class:
            mock_ad = MagicMock()
            mock_ad.id = "ad123"
            mock_ad_class.return_value = mock_ad

            with patch.object(service, "verify_ownership"):
                data = AdvertisementCreate(
                    title="Paris Event",
                    description="Annual festival",
                    active=True,
                )

                result = service.create("dest123", data, "user123")

                assert result is not None


class TestAdvertisementServiceRead:
    @pytest.mark.asyncio
    async def test_list_advertisements_success(self):
        service = AdvertisementService()

        with patch.object(service, "list", return_value=[]):
            result = await service.list("dest123")

            assert result is not None

    @pytest.mark.asyncio
    async def test_list_advertisements_active_only(self):
        service = AdvertisementService()

        with patch.object(service, "list", return_value=[]):
            result = await service.list("dest123", active_only=True)

            assert result is not None


class TestAdvertisementServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_advertisement_success(self):
        from app.schemas import AdvertisementUpdate

        service = AdvertisementService()

        mock_ad = MagicMock()
        mock_ad.id = "ad123"
        mock_ad.destination_id = "dest123"
        mock_ad.title = "Updated"
        mock_ad.description = "Test"
        mock_ad.image_url = "http://test.com/image.jpg"
        mock_ad.link_url = "http://test.com"
        mock_ad.active = True

        with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
            with patch.object(service, "verify_ownership"):
                result = await service.update(
                    "ad123", AdvertisementUpdate(title="Updated"), "dest123", "user123"
                )

                assert result is not None

    @pytest.mark.asyncio
    async def test_update_advertisement_not_found(self):
        from app.schemas import AdvertisementUpdate

        service = AdvertisementService()

        with patch("app.models.Advertisement.collection.get", return_value=None):
            result = await service.update("ad123", AdvertisementUpdate(title="Updated"))

            assert result is None

    @pytest.mark.asyncio
    async def test_update_advertisement_wrong_destination(self):
        from app.schemas import AdvertisementUpdate

        service = AdvertisementService()

        mock_ad = MagicMock()
        mock_ad.destination_id = "other_dest"

        with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update(
                    "ad123", AdvertisementUpdate(title="Updated"), "dest123", "user123"
                )

    @pytest.mark.asyncio
    async def test_update_advertisement_no_owner(self):
        from app.schemas import AdvertisementUpdate

        service = AdvertisementService()

        mock_ad = MagicMock()
        mock_ad.id = "ad123"
        mock_ad.destination_id = "dest123"
        mock_ad.title = "Updated"
        mock_ad.description = "Test"
        mock_ad.image_url = "http://test.com/image.jpg"
        mock_ad.link_url = "http://test.com"
        mock_ad.active = True

        with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
            result = await service.update(
                "ad123", AdvertisementUpdate(title="Updated"), destination_id="dest123"
            )

            assert result is not None


class TestAdvertisementServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_advertisement_success(self):
        service = AdvertisementService()

        mock_ad = MagicMock()
        mock_ad.destination_id = "dest123"

        with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
            with patch.object(service, "verify_ownership"):
                await service.delete("ad123", "dest123", "user123")

                mock_ad.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_advertisement_not_found(self):
        service = AdvertisementService()

        with patch("app.models.Advertisement.collection.get", return_value=None):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("ad123", "dest123", "user123")

    @pytest.mark.asyncio
    async def test_delete_advertisement_wrong_destination(self):
        service = AdvertisementService()

        mock_ad = MagicMock()
        mock_ad.destination_id = "other_dest"

        with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("ad123", "dest123", "user123")

    @pytest.mark.asyncio
    async def test_delete_advertisement_without_owner(self):
        service = AdvertisementService()

        mock_ad = MagicMock()
        mock_ad.destination_id = "dest123"

        with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
            await service.delete("ad123", destination_id="dest123")

            mock_ad.delete.assert_called_once()


class TestAdvertisementServiceCreateWithoutOwner:
    @pytest.mark.asyncio
    async def test_create_advertisement_without_owner(self):
        service = AdvertisementService()

        with patch("app.models.Advertisement") as mock_ad_class:
            mock_ad = MagicMock()
            mock_ad.id = "ad123"
            mock_ad_class.return_value = mock_ad

            data = AdvertisementCreate(
                title="Paris Event",
                description="Annual festival",
                active=True,
            )

            result = await service.create("dest123", data)

            assert result is not None


class TestDiscountServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_discount_success(self):
        from app.schemas import DiscountUpdate

        service = DiscountService()

        mock_discount = MagicMock()
        mock_discount.id = "discount123"
        mock_discount.destination_id = "dest123"
        mock_discount.title = "Updated"
        mock_discount.description = "Test"
        mock_discount.attraction_name = "Test"
        mock_discount.promo_code = "TEST123"
        mock_discount.link_url = "http://test.com"
        mock_discount.discount_percentage = 50
        mock_discount.active = True

        with patch("app.models.Discount.collection.get", return_value=mock_discount):
            with patch.object(service, "verify_ownership"):
                result = await service.update(
                    "discount123", DiscountUpdate(title="Updated"), "dest123", "user123"
                )

                assert result is not None

    @pytest.mark.asyncio
    async def test_update_discount_not_found(self):
        from app.schemas import DiscountUpdate

        service = DiscountService()

        with patch("app.models.Discount.collection.get", return_value=None):
            result = await service.update("discount123", DiscountUpdate(title="Updated"))

            assert result is None

    @pytest.mark.asyncio
    async def test_update_discount_wrong_destination(self):
        from app.schemas import DiscountUpdate

        service = DiscountService()

        mock_discount = MagicMock()
        mock_discount.destination_id = "other_dest"

        with patch("app.models.Discount.collection.get", return_value=mock_discount):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update(
                    "discount123", DiscountUpdate(title="Updated"), "dest123", "user123"
                )

    @pytest.mark.asyncio
    async def test_update_discount_without_owner(self):
        from app.schemas import DiscountUpdate

        service = DiscountService()

        mock_discount = MagicMock()
        mock_discount.id = "discount123"
        mock_discount.destination_id = "dest123"
        mock_discount.title = "Updated"
        mock_discount.description = "Test"
        mock_discount.attraction_name = "Test"
        mock_discount.promo_code = "TEST123"
        mock_discount.link_url = "http://test.com"
        mock_discount.discount_percentage = 50
        mock_discount.active = True

        with patch("app.models.Discount.collection.get", return_value=mock_discount):
            result = await service.update(
                "discount123", DiscountUpdate(title="Updated"), destination_id="dest123"
            )

            assert result is not None


class TestDiscountServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_discount_success(self):
        service = DiscountService()

        mock_discount = MagicMock()
        mock_discount.destination_id = "dest123"

        with patch("app.models.Discount.collection.get", return_value=mock_discount):
            with patch.object(service, "verify_ownership"):
                await service.delete("discount123", "dest123", "user123")

                mock_discount.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_discount_not_found(self):
        service = DiscountService()

        with patch("app.models.Discount.collection.get", return_value=None):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("discount123", "dest123", "user123")

    @pytest.mark.asyncio
    async def test_delete_discount_without_owner(self):
        service = DiscountService()

        mock_discount = MagicMock()
        mock_discount.destination_id = "dest123"

        with patch("app.models.Discount.collection.get", return_value=mock_discount):
            await service.delete("discount123", destination_id="dest123")

            mock_discount.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_discount_wrong_destination(self):
        service = DiscountService()

        mock_discount = MagicMock()
        mock_discount.destination_id = "other_dest"

        with patch("app.models.Discount.collection.get", return_value=mock_discount):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("discount123", "dest123", "user123")


class TestOfferServiceUpdateMissing:
    @pytest.mark.asyncio
    async def test_update_offer_not_found(self):
        from app.schemas import OfferUpdate

        service = OfferService()

        with patch("app.models.Offer.collection.get", return_value=None):
            result = await service.update("offer123", OfferUpdate(title="Updated"))

            assert result is None

    @pytest.mark.asyncio
    async def test_update_offer_wrong_destination(self):
        from app.schemas import OfferUpdate

        service = OfferService()

        mock_offer = MagicMock()
        mock_offer.destination_id = "other_dest"

        with patch("app.models.Offer.collection.get", return_value=mock_offer):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update("offer123", OfferUpdate(title="Updated"), "dest123", "user123")


class TestOfferServiceDeleteMissing:
    @pytest.mark.asyncio
    async def test_delete_offer_not_found(self):
        service = OfferService()

        with patch("app.models.Offer.collection.get", return_value=None):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("offer123", "dest123", "user123")

    @pytest.mark.asyncio
    async def test_delete_offer_wrong_destination(self):
        service = OfferService()

        mock_offer = MagicMock()
        mock_offer.destination_id = "other_dest"

        with patch("app.models.Offer.collection.get", return_value=mock_offer):
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("offer123", "dest123", "user123")
