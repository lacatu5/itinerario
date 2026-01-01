from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models import (
    Advertisement,
    Destination as DestinationModel,
    Discount,
    Offer,
)


class TestDestinationEndpoints:
    @pytest.mark.asyncio
    async def test_create_destination_success(self, client):
        with patch("app.models.Destination") as mock_destination_class:
            mock_destination = MagicMock()
            mock_destination.id = "dest123"
            mock_destination.owner_id = "test_firebase_uid_123"
            mock_destination.name = "Paris"
            mock_destination.region = "Île-de-France"
            mock_destination.country = "France"
            mock_destination.description = "Beautiful city"
            mock_destination.image_url = None
            mock_destination.latitude = None
            mock_destination.longitude = None
            mock_destination.address = None
            mock_destination.created_at = datetime.now()
            mock_destination.updated_at = None
            mock_destination_class.return_value = mock_destination

            response = await client.post(
                "/api/destinations/",
                json={
                    "name": "Paris",
                    "region": "Île-de-France",
                    "country": "France",
                    "short_description": "Beautiful city",
                    "detail_description": "Detailed description",
                },
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_destinations_success(self, client):
        with patch.object(DestinationModel, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query
            mock_collection.offset.return_value = mock_query

            response = await client.get("/api/destinations/")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_destinations_with_pagination(self, client):
        with patch.object(DestinationModel, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query
            mock_collection.offset.return_value = mock_query

            response = await client.get("/api/destinations/?skip=10&limit=20")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_destination_with_content_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "user123"
        mock_destination.name = "Paris"
        mock_destination.region = "Île-de-France"
        mock_destination.country = "France"
        mock_destination.description = "Beautiful city"
        mock_destination.image_url = None
        mock_destination.latitude = None
        mock_destination.longitude = None
        mock_destination.address = None
        mock_destination.created_at = datetime.now()
        mock_destination.updated_at = None

        async def mock_list(*args, **kwargs):
            return MagicMock(items=[], total_count=0)

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.AdvertisementService") as mock_ad_service:
                mock_ad_service.return_value.list = mock_list
                with patch("app.services.OfferService") as mock_offer_service:
                    mock_offer_service.return_value.list = mock_list
                    with patch("app.services.DiscountService") as mock_discount_service:
                        mock_discount_service.return_value.list = mock_list

                        response = await client.get("/api/destinations/dest123")

                        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_destination_not_found(self, client):
        with patch("app.models.Destination.collection.get", return_value=None):
            response = await client.get("/api/destinations/nonexistent")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_destination_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"
        mock_destination.name = "Updated Paris"
        mock_destination.region = "Île-de-France"
        mock_destination.country = "France"
        mock_destination.description = "Updated description"
        mock_destination.image_url = None
        mock_destination.latitude = None
        mock_destination.longitude = None
        mock_destination.address = None
        mock_destination.created_at = datetime.now()
        mock_destination.updated_at = datetime.now()

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                response = await client.put(
                    "/api/destinations/dest123",
                    json={"name": "Updated Paris"},
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_destination_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"
        mock_destination.delete = MagicMock()

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                response = await client.delete("/api/destinations/dest123")

                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_upload_destination_image_success(self, client):
        from app.services import DestinationService

        mock_result = {
            "message": "Destination image uploaded successfully",
            "destination": MagicMock(
                id="dest123",
                name="Paris",
                region="Île-de-France",
                country="France",
                description="Beautiful",
                image_url="https://example.com/image.jpg",
            ),
        }

        with patch.object(DestinationService, "upload_destination_image", return_value=mock_result):
            response = await client.post(
                "/api/destinations/dest123/upload-image",
                files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_destination_image_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"
        mock_destination.image_url = "https://example.com/image.jpg"
        mock_destination.name = "Paris"
        mock_destination.region = "Île-de-France"
        mock_destination.country = "France"
        mock_destination.description = "Beautiful"
        mock_destination.latitude = None
        mock_destination.longitude = None
        mock_destination.address = None
        mock_destination.created_at = datetime.now()
        mock_destination.updated_at = None

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.services.delete_image"):
                    response = await client.delete("/api/destinations/dest123/image")

                    assert response.status_code == 204


class TestAdvertisementEndpoints:
    @pytest.mark.asyncio
    async def test_create_advertisement_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Advertisement") as mock_ad_class:
                    mock_ad = MagicMock()
                    mock_ad.id = "ad123"
                    mock_ad.destination_id = "dest123"
                    mock_ad.title = "Paris Event"
                    mock_ad.description = "Annual festival"
                    mock_ad.image_url = None
                    mock_ad.link_url = None
                    mock_ad.active = True
                    mock_ad.created_at = datetime.now()
                    mock_ad_class.return_value = mock_ad

                    response = await client.post(
                        "/api/destinations/dest123/advertisements",
                        json={
                            "title": "Paris Event",
                            "description": "Annual festival",
                            "active": True,
                        },
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_advertisements_success(self, client):
        with patch.object(Advertisement, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query

            response = await client.get("/api/destinations/dest123/advertisements")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_advertisements_active_only(self, client):
        with patch.object(Advertisement, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query

            response = await client.get("/api/destinations/dest123/advertisements?active_only=true")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_advertisement_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"

        mock_ad = MagicMock()
        mock_ad.id = "ad123"
        mock_ad.destination_id = "dest123"
        mock_ad.title = "Updated Event"
        mock_ad.description = "Test description"
        mock_ad.image_url = "http://test.com/image.jpg"
        mock_ad.link_url = "http://test.com"
        mock_ad.active = True

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
                    response = await client.put(
                        "/api/destinations/dest123/advertisements/ad123",
                        json={"title": "Updated Event"},
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_advertisement_success(self, client):
        mock_destination = MagicMock()
        mock_destination.owner_id = "test_firebase_uid_123"

        mock_ad = MagicMock()
        mock_ad.id = "ad123"
        mock_ad.destination_id = "dest123"
        mock_ad.delete = MagicMock()

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Advertisement.collection.get", return_value=mock_ad):
                    response = await client.delete("/api/destinations/dest123/advertisements/ad123")

                    assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_advertisement_not_found(self, client):
        mock_destination = MagicMock()
        mock_destination.owner_id = "test_firebase_uid_123"

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Advertisement.collection.get", return_value=None):
                    response = await client.delete("/api/destinations/dest123/advertisements/ad123")

                    assert response.status_code == 404


class TestDiscountEndpoints:
    @pytest.mark.asyncio
    async def test_create_discount_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Discount") as mock_discount_class:
                    mock_discount = MagicMock()
                    mock_discount.id = "discount123"
                    mock_discount.destination_id = "dest123"
                    mock_discount.title = "Museum Discount"
                    mock_discount.description = "50% off"
                    mock_discount.attraction_name = "Louvre"
                    mock_discount.discount_percentage = 50
                    mock_discount.promo_code = "LOUVRE50"
                    mock_discount.link_url = None
                    mock_discount.active = True
                    mock_discount.created_at = datetime.now()
                    mock_discount_class.return_value = mock_discount

                    response = await client.post(
                        "/api/destinations/dest123/discounts",
                        json={
                            "title": "Museum Discount",
                            "description": "50% off",
                            "attraction_name": "Louvre",
                            "discount_percentage": 50,
                            "active": True,
                        },
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_discounts_success(self, client):
        with patch.object(Discount, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query

            response = await client.get("/api/destinations/dest123/discounts")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_discounts_active_only(self, client):
        with patch.object(Discount, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query

            response = await client.get("/api/destinations/dest123/discounts?active_only=true")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_discount_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"

        mock_discount = MagicMock()
        mock_discount.id = "discount123"
        mock_discount.destination_id = "dest123"
        mock_discount.title = "Updated Discount"
        mock_discount.description = "Test description"
        mock_discount.attraction_name = "Test"
        mock_discount.promo_code = "TEST123"
        mock_discount.link_url = "http://test.com"
        mock_discount.discount_percentage = 50
        mock_discount.active = True

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Discount.collection.get", return_value=mock_discount):
                    response = await client.put(
                        "/api/destinations/dest123/discounts/discount123",
                        json={"title": "Updated Discount"},
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_discount_success(self, client):
        mock_destination = MagicMock()
        mock_destination.owner_id = "test_firebase_uid_123"

        mock_discount = MagicMock()
        mock_discount.id = "discount123"
        mock_discount.destination_id = "dest123"
        mock_discount.delete = MagicMock()

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Discount.collection.get", return_value=mock_discount):
                    response = await client.delete(
                        "/api/destinations/dest123/discounts/discount123"
                    )

                    assert response.status_code == 204


class TestOfferEndpoints:
    @pytest.mark.asyncio
    async def test_create_offer_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Offer") as mock_offer_class:
                    mock_offer = MagicMock()
                    mock_offer.id = "offer123"
                    mock_offer.destination_id = "dest123"
                    mock_offer.title = "Special Offer"
                    mock_offer.description = "Great deal"
                    mock_offer.accommodation_name = "Hotel Paris"
                    mock_offer.price = None
                    mock_offer.discount_percentage = None
                    mock_offer.valid_from = None
                    mock_offer.valid_until = None
                    mock_offer.image_url = None
                    mock_offer.link_url = None
                    mock_offer.active = True
                    mock_offer.created_at = datetime.now()
                    mock_offer_class.return_value = mock_offer

                    response = await client.post(
                        "/api/destinations/dest123/offers",
                        json={
                            "title": "Special Offer",
                            "description": "Great deal",
                            "accommodation_name": "Hotel Paris",
                            "active": True,
                        },
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_offers_success(self, client):
        with patch.object(Offer, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query

            response = await client.get("/api/destinations/dest123/offers")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_offers_active_only(self, client):
        with patch.object(Offer, "collection") as mock_collection:
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_collection.where.return_value = mock_query
            mock_collection.order_by.return_value = mock_query
            mock_collection.limit.return_value = mock_query

            response = await client.get("/api/destinations/dest123/offers?active_only=true")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_offer_success(self, client):
        mock_destination = MagicMock()
        mock_destination.id = "dest123"
        mock_destination.owner_id = "test_firebase_uid_123"

        mock_offer = MagicMock()
        mock_offer.id = "offer123"
        mock_offer.destination_id = "dest123"
        mock_offer.title = "Updated Offer"
        mock_offer.description = "Test description"
        mock_offer.accommodation_name = "Test Hotel"
        mock_offer.price = 100
        mock_offer.discount_percentage = 20
        mock_offer.valid_from = datetime.now()
        mock_offer.valid_until = datetime.now()
        mock_offer.image_url = "http://test.com/image.jpg"
        mock_offer.link_url = "http://test.com"
        mock_offer.active = True

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Offer.collection.get", return_value=mock_offer):
                    response = await client.put(
                        "/api/destinations/dest123/offers/offer123",
                        json={"title": "Updated Offer"},
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_offer_success(self, client):
        mock_destination = MagicMock()
        mock_destination.owner_id = "test_firebase_uid_123"

        mock_offer = MagicMock()
        mock_offer.id = "offer123"
        mock_offer.destination_id = "dest123"
        mock_offer.delete = MagicMock()

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Offer.collection.get", return_value=mock_offer):
                    response = await client.delete("/api/destinations/dest123/offers/offer123")

                    assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_offer_not_found(self, client):
        mock_destination = MagicMock()
        mock_destination.owner_id = "test_firebase_uid_123"

        with patch("app.models.Destination.collection.get", return_value=mock_destination):
            with patch("app.services.verify_ownership"):
                with patch("app.models.Offer.collection.get", return_value=None):
                    response = await client.delete("/api/destinations/dest123/offers/offer123")

                    assert response.status_code == 404
