from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import AuthorizationException

from app.schemas import (
    ItineraryCreate,
    ItineraryUpdate,
    LocationCreate,
    LocationUpdate,
    TransportCreate,
    TransportUpdate,
)
from app.services import ItineraryService, LocationService, TransportService
from core.exceptions import EntityNotFoundException, ValidationException


@pytest.fixture
def mock_user_resolver():
    with patch("app.services.UserResolver") as mock:
        resolver_instance = AsyncMock()
        resolver_instance.get_user_id.return_value = 123
        mock.return_value = resolver_instance
        yield resolver_instance


@pytest.fixture
def sample_itinerary_dict():
    return {
        "id": 1,
        "title": "Test Trip",
        "destination": "Paris",
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 6, 10),
        "short_description": "Test",
        "detail_description": "Test details",
        "image_url": None,
        "latitude": None,
        "longitude": None,
        "address": None,
        "owner_id": 123,
        "created_at": datetime.now(),
    }


class TestItineraryServiceCreate:
    @pytest.mark.asyncio
    async def test_create_itinerary_success(self, mock_user_resolver):
        mock_db = AsyncMock(spec=AsyncSession)

        async def mock_refresh(obj):
            obj.id = 1
            obj.created_at = datetime.now()

        mock_db.refresh = mock_refresh

        service = ItineraryService(mock_db)
        itinerary_data = ItineraryCreate(
            title="Test Trip",
            destination="Paris",
            start_date=date(2024, 6, 1),
            short_description="Test",
            detail_description="Test details",
        )

        result = await service.create_itinerary(itinerary_data, "user_id")

        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_itinerary_invalid_dates(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with pytest.raises(ValidationError, match="end_date must be on or after start_date"):
            ItineraryCreate(
                title="Test Trip",
                destination="Paris",
                start_date=date(2024, 6, 10),
                end_date=date(2024, 6, 1),
                short_description="Test",
                detail_description="Test details",
            )

    def test_create_itinerary_with_valid_dates(self):
        itinerary = ItineraryCreate(
            title="Test Trip",
            destination="Paris",
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 10),
            short_description="Test",
            detail_description="Test details",
        )
        assert itinerary.end_date == date(2024, 6, 10)

    def test_create_itinerary_with_null_end_date(self):
        itinerary = ItineraryCreate(
            title="Test Trip",
            destination="Paris",
            start_date=date(2024, 6, 1),
            short_description="Test",
            detail_description="Test details",
        )
        assert itinerary.end_date is None


class TestItineraryServiceRead:
    @pytest.mark.asyncio
    async def test_list_itineraries_with_user_id(self):
        mock_db = AsyncMock(spec=AsyncSession)

        async def mock_paginate(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.items = []
            mock_result.total = 0
            return mock_result

        with patch("app.services.paginate", side_effect=mock_paginate):
            service = ItineraryService(mock_db)
            result = await service.list_itineraries("user_id")

    @pytest.mark.asyncio
    async def test_get_itinerary_with_owner_success(self, sample_itinerary_dict):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock(**sample_itinerary_dict)

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            service = ItineraryService(mock_db)
            result = await service.get_itinerary_with_owner_public(1)

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_itinerary_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = ItineraryService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get_itinerary_with_owner_public(999)


class TestItineraryServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_itinerary_success(self, mock_user_resolver):
        from app.schemas import ItineraryUpdate

        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.id = 1
        mock_itinerary.title = "Updated"
        mock_itinerary.destination = "Paris"
        mock_itinerary.start_date = date(2024, 6, 1)
        mock_itinerary.end_date = date(2024, 6, 10)
        mock_itinerary.short_description = "Test"
        mock_itinerary.detail_description = "Test details"
        mock_itinerary.image_url = None
        mock_itinerary.latitude = None
        mock_itinerary.longitude = None
        mock_itinerary.address = None
        mock_itinerary.owner_id = 123
        mock_itinerary.created_at = datetime.now()

        with patch.object(ItineraryService, "verify_ownership", return_value=mock_itinerary):
            service = ItineraryService(mock_db)
            update_data = ItineraryUpdate(title="Updated")
            result = await service.update_itinerary(1, update_data, "user_id")

            assert result is not None
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_itinerary_not_authorized(self, mock_user_resolver):
        from app.schemas import ItineraryUpdate

        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            ItineraryService,
            "verify_ownership",
            side_effect=EntityNotFoundException("Itinerary 1 not found"),
        ):
            service = ItineraryService(mock_db)
            update_data = ItineraryUpdate(title="Updated")

            with pytest.raises(EntityNotFoundException):
                await service.update_itinerary(1, update_data, "user_id")


class TestItineraryServiceImage:
    @pytest.mark.asyncio
    async def test_upload_itinerary_image_success(self, mock_user_resolver):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()

        with patch.object(ItineraryService, "verify_ownership", return_value=mock_itinerary):
            with patch("app.services.sync_model_image") as mock_sync:
                mock_sync.return_value = {"image_url": "https://example.com/image.jpg"}

                service = ItineraryService(mock_db)
                result = await service.upload_itinerary_image(1, "user_id", MagicMock())

                mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_itinerary_image_not_authorized(self, mock_user_resolver):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            ItineraryService,
            "verify_ownership",
            side_effect=EntityNotFoundException("Itinerary 1 not found"),
        ):
            service = ItineraryService(mock_db)

            with pytest.raises(EntityNotFoundException):
                await service.upload_itinerary_image(1, "user_id", MagicMock())


class TestLocationServiceCreate:
    @pytest.mark.asyncio
    async def test_create_location_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = "user_id"

        async def mock_refresh(obj):
            obj.id = 1
            obj.created_at = datetime.now()

        mock_db.refresh = mock_refresh

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            service = LocationService(mock_db)
            location_data = LocationCreate(
                name="Eiffel Tower",
                short_description="Famous landmark",
                from_date=date(2024, 6, 1),
                to_date=date(2024, 6, 1),
            )

            with patch("app.services.verify_resource_ownership"):
                result = await service.create(location_data, 1, "user_id")

    @pytest.mark.asyncio
    async def test_create_location_invalid_dates(self):
        mock_db = AsyncMock(spec=AsyncSession)

        service = LocationService(mock_db)

        with pytest.raises(ValueError, match="to_date must be on or after from_date"):
            LocationCreate(
                name="Test",
                short_description="Test",
                from_date=date(2024, 6, 10),
                to_date=date(2024, 6, 1),
            )


class TestLocationServiceRead:
    @pytest.mark.asyncio
    async def test_get_location_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.configure_mock(
            id=1,
            name="Eiffel Tower",
            short_description="Famous landmark",
            from_date=date(2024, 6, 1),
            to_date=date(2024, 6, 1),
            image_url=None,
            latitude=None,
            longitude=None,
            address=None,
            itinerary_id=1,
        )

        with patch.object(mock_db, "get", return_value=mock_location):
            service = LocationService(mock_db)
            result = await service.get(1)

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_location_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = LocationService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get(999)


class TestLocationServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_location_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.configure_mock(
            id=1,
            name="Updated Name",
            short_description="Famous landmark",
            from_date=date(2024, 6, 1),
            to_date=date(2024, 6, 1),
            image_url=None,
            latitude=None,
            longitude=None,
            address=None,
            itinerary_id=1,
        )

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=mock_location):
                service = LocationService(mock_db)
                location_data = LocationUpdate(name="Updated Name")

                result = await service.update(1, location_data, "user_id")

    @pytest.mark.asyncio
    async def test_update_location_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = LocationService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update(999, LocationUpdate(name="Updated"), "user_id")


class TestLocationServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_location_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.id = 1

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch("sqlalchemy.ext.asyncio.AsyncSession.get", return_value=mock_location):
                service = LocationService(mock_db)
                await service.delete(1, "user_id")

    @pytest.mark.asyncio
    async def test_delete_location_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = LocationService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete(999, "user_id")

    @pytest.mark.asyncio
    async def test_delete_location_image_no_image(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.configure_mock(
            id=1,
            name="Test",
            short_description="Test",
            from_date=date(2024, 6, 1),
            to_date=date(2024, 6, 1),
            image_url=None,
            latitude=None,
            longitude=None,
            address=None,
            itinerary_id=1,
        )

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=mock_location):
                service = LocationService(mock_db)

                with pytest.raises(ValidationException, match="has no image"):
                    await service.delete_image(1, "user_id")


class TestTransportServiceCreate:
    @pytest.mark.asyncio
    async def test_create_transport_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = "user_id"

        async def mock_refresh(obj):
            obj.id = 1
            obj.transport_number = None
            obj.created_at = datetime.now()

        mock_db.refresh = mock_refresh

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            service = TransportService(mock_db)
            transport_data = TransportCreate(
                type="flight",
                departure_location="JFK",
                arrival_location="CDG",
                departure_time=datetime(2024, 6, 1, 10, 0),
                arrival_time=datetime(2024, 6, 1, 22, 0),
            )

            with patch("app.services.verify_resource_ownership"):
                result = await service.create(transport_data, 1, "user_id")

    @pytest.mark.asyncio
    async def test_create_transport_invalid_times(self):
        mock_db = AsyncMock(spec=AsyncSession)

        service = TransportService(mock_db)

        with pytest.raises(ValueError, match="arrival_time must be after departure_time"):
            TransportCreate(
                type="flight",
                departure_location="JFK",
                arrival_location="CDG",
                departure_time=datetime(2024, 6, 1, 22, 0),
                arrival_time=datetime(2024, 6, 1, 10, 0),
            )


class TestTransportServiceRead:
    @pytest.mark.asyncio
    async def test_get_transport_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_transport = MagicMock()
        mock_transport.configure_mock(
            id=1,
            type="flight",
            departure_location="JFK",
            arrival_location="CDG",
            departure_time=datetime(2024, 6, 1, 10, 0),
            arrival_time=datetime(2024, 6, 1, 22, 0),
            carrier=None,
            price=None,
            transport_number=None,
            itinerary_id=1,
        )

        with patch.object(mock_db, "get", return_value=mock_transport):
            service = TransportService(mock_db)
            result = await service.get(1)

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_transport_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = TransportService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get(999)


class TestTransportServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_transport_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_transport = MagicMock()
        mock_transport.configure_mock(
            id=1,
            type="flight",
            departure_location="JFK",
            arrival_location="CDG",
            departure_time=datetime(2024, 6, 1, 10, 0),
            arrival_time=datetime(2024, 6, 1, 22, 0),
            carrier="Updated Airline",
            price=None,
            transport_number=None,
            itinerary_id=1,
        )

        with patch.object(
            TransportService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=mock_transport):
                service = TransportService(mock_db)
                transport_data = TransportUpdate(carrier="Updated Airline")

                result = await service.update(1, transport_data, "user_id")

    @pytest.mark.asyncio
    async def test_update_transport_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = TransportService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update(999, TransportUpdate(carrier="Updated"), "user_id")


class TestTransportServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_transport_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_transport = MagicMock()
        mock_transport.id = 1

        with patch.object(
            TransportService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch("sqlalchemy.ext.asyncio.AsyncSession.get", return_value=mock_transport):
                service = TransportService(mock_db)
                await service.delete(1, "user_id")

    @pytest.mark.asyncio
    async def test_delete_transport_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = TransportService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete(999, "user_id")


class TestItineraryServiceSearch:
    @pytest.mark.asyncio
    async def test_search_itineraries_with_all_filters(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_scalar_result = MagicMock()
        mock_scalar_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_scalar_result
        mock_db.execute.return_value = mock_result

        service = ItineraryService(mock_db)
        result = await service.search_itineraries_with_owners(
            destination="Paris",
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 10),
            search_text="test trip",
            skip=0,
            limit=10,
        )

        assert "results" in result
        assert "total" in result

    @pytest.mark.asyncio
    async def test_search_itineraries_with_only_destination(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = ItineraryService(mock_db)
        result = await service.search_itineraries_with_owners(destination="Paris")

        assert "results" in result

    @pytest.mark.asyncio
    async def test_search_itineraries_with_only_date_range(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = ItineraryService(mock_db)
        result = await service.search_itineraries_with_owners(
            start_date=date(2024, 6, 1), end_date=date(2024, 6, 10)
        )

        assert "results" in result

    @pytest.mark.asyncio
    async def test_search_itineraries_with_only_start_date(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = ItineraryService(mock_db)
        result = await service.search_itineraries_with_owners(start_date=date(2024, 6, 1))

        assert "results" in result

    @pytest.mark.asyncio
    async def test_search_itineraries_with_only_end_date(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = ItineraryService(mock_db)
        result = await service.search_itineraries_with_owners(end_date=date(2024, 6, 10))

        assert "results" in result

    @pytest.mark.asyncio
    async def test_search_itineraries_no_filters(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = ItineraryService(mock_db)
        result = await service.search_itineraries_with_owners()

        assert "results" in result

    @pytest.mark.asyncio
    async def test_get_itinerary_locations_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        async def mock_paginate(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.items = []
            mock_result.total = 0
            return mock_result

        with patch("app.services.paginate", side_effect=mock_paginate):
            service = ItineraryService(mock_db)
            result = await service.get_itinerary_locations(1)

    @pytest.mark.asyncio
    async def test_get_itinerary_transports_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        async def mock_paginate(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.items = []
            mock_result.total = 0
            return mock_result

        with patch("app.services.paginate", side_effect=mock_paginate):
            service = ItineraryService(mock_db)
            result = await service.get_itinerary_transports(1)


class TestItineraryServiceOwnership:
    @pytest.mark.asyncio
    async def test_verify_ownership_success(self, mock_user_resolver):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = 123

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            with patch("app.services.verify_resource_ownership"):
                service = ItineraryService(mock_db)
                result = await service.verify_ownership(1, "user_id")

                assert result is not None

    @pytest.mark.asyncio
    async def test_verify_ownership_not_found(self, mock_user_resolver):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = ItineraryService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.verify_ownership(999, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_unauthorized(self, mock_user_resolver):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = 456

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            with patch("app.services.verify_resource_ownership") as mock_verify:
                from core.exceptions import AuthorizationException

                mock_verify.side_effect = AuthorizationException("Not authorized")

                service = ItineraryService(mock_db)

                with pytest.raises(AuthorizationException):
                    await service.verify_ownership(1, "user_id")


class TestLocationServiceAdditional:
    @pytest.mark.asyncio
    async def test_get_by_itinerary_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = LocationService(mock_db)
        result = await service.get_by_itinerary(1)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_by_itinerary_with_pagination(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = LocationService(mock_db)
        result = await service.get_by_itinerary(1, skip=10, limit=20)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_update_image_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.image_url = "http://example.com/old.jpg"

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch("sqlalchemy.ext.asyncio.AsyncSession.get", return_value=mock_location):
                with patch("app.services.sync_model_image") as mock_sync:
                    mock_sync.return_value = {"image_url": "http://example.com/new.jpg"}

                    service = LocationService(mock_db)
                    result = await service.update_image(1, MagicMock(), "user_id")

                    mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_location_itinerary_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = LocationService(mock_db)
            location_data = LocationCreate(
                name="Eiffel Tower",
                short_description="Famous landmark",
                from_date=date(2024, 6, 1),
                to_date=date(2024, 6, 1),
            )

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.create(location_data, 999, "user_id")

    @pytest.mark.asyncio
    async def test_create_location_unauthorized(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = "other_user_id"

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            with patch("app.services.verify_resource_ownership") as mock_verify:
                mock_verify.side_effect = AuthorizationException("Not authorized")

                service = LocationService(mock_db)
                location_data = LocationCreate(
                    name="Eiffel Tower",
                    short_description="Famous landmark",
                    from_date=date(2024, 6, 1),
                    to_date=date(2024, 6, 1),
                )

                with pytest.raises(AuthorizationException):
                    await service.create(location_data, 1, "user_id")

    @pytest.mark.asyncio
    async def test_delete_image_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.configure_mock(
            id=1,
            name="Test",
            short_description="Test",
            from_date=date(2024, 6, 1),
            to_date=date(2024, 6, 1),
            image_url="http://example.com/image.jpg",
            latitude=None,
            longitude=None,
            address=None,
            itinerary_id=1,
        )

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=mock_location):
                with patch("app.services.delete_image"):
                    service = LocationService(mock_db)
                    await service.delete_image(1, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_and_get_itinerary_location_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = LocationService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.verify_ownership_and_get_itinerary(999, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_and_get_itinerary_itinerary_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.itinerary_id = 1

        with patch.object(mock_db, "get") as mock_get:
            mock_get.side_effect = [mock_location, None]

            service = LocationService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.verify_ownership_and_get_itinerary(1, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_and_get_itinerary_unauthorized(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_location = MagicMock()
        mock_location.itinerary_id = 1

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = "other_user_id"

        with patch.object(mock_db, "get") as mock_get:
            mock_get.side_effect = [mock_location, mock_itinerary]

            with patch("app.services.verify_resource_ownership") as mock_verify:
                mock_verify.side_effect = AuthorizationException("Not authorized")

                service = LocationService(mock_db)

                with pytest.raises(AuthorizationException):
                    await service.verify_ownership_and_get_itinerary(1, "user_id")


class TestTransportServiceAdditional:
    @pytest.mark.asyncio
    async def test_get_by_itinerary_success(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = TransportService(mock_db)
        result = await service.get_by_itinerary(1)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_by_itinerary_with_pagination(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = TransportService(mock_db)
        result = await service.get_by_itinerary(1, skip=10, limit=20)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_create_transport_itinerary_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = TransportService(mock_db)
            transport_data = TransportCreate(
                type="flight",
                departure_location="JFK",
                arrival_location="CDG",
                departure_time=datetime(2024, 6, 1, 10, 0),
                arrival_time=datetime(2024, 6, 1, 22, 0),
            )

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.create(transport_data, 999, "user_id")

    @pytest.mark.asyncio
    async def test_create_transport_unauthorized(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = "other_user_id"

        with patch.object(mock_db, "get", return_value=mock_itinerary):
            with patch("app.services.verify_resource_ownership") as mock_verify:
                mock_verify.side_effect = AuthorizationException("Not authorized")

                service = TransportService(mock_db)
                transport_data = TransportCreate(
                    type="flight",
                    departure_location="JFK",
                    arrival_location="CDG",
                    departure_time=datetime(2024, 6, 1, 10, 0),
                    arrival_time=datetime(2024, 6, 1, 22, 0),
                )

                with pytest.raises(AuthorizationException):
                    await service.create(transport_data, 1, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_and_get_itinerary_transport_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(mock_db, "get", return_value=None):
            service = TransportService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.verify_ownership_and_get_itinerary(999, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_and_get_itinerary_itinerary_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_transport = MagicMock()
        mock_transport.itinerary_id = 1

        with patch.object(mock_db, "get") as mock_get:
            mock_get.side_effect = [mock_transport, None]

            service = TransportService(mock_db)

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.verify_ownership_and_get_itinerary(1, "user_id")

    @pytest.mark.asyncio
    async def test_verify_ownership_and_get_itinerary_unauthorized(self):
        mock_db = AsyncMock(spec=AsyncSession)

        mock_transport = MagicMock()
        mock_transport.itinerary_id = 1

        mock_itinerary = MagicMock()
        mock_itinerary.owner_id = "other_user_id"

        with patch.object(mock_db, "get") as mock_get:
            mock_get.side_effect = [mock_transport, mock_itinerary]

            with patch("app.services.verify_resource_ownership") as mock_verify:
                mock_verify.side_effect = AuthorizationException("Not authorized")

                service = TransportService(mock_db)

                with pytest.raises(AuthorizationException):
                    await service.verify_ownership_and_get_itinerary(1, "user_id")


class TestItineraryServiceListAll:
    @pytest.mark.asyncio
    async def test_list_itineraries_no_user_id(self):
        mock_db = AsyncMock(spec=AsyncSession)

        async def mock_paginate(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.items = []
            mock_result.total = 0
            return mock_result

        with patch("app.services.paginate", side_effect=mock_paginate):
            service = ItineraryService(mock_db)
            result = await service.list_itineraries(None)

    @pytest.mark.asyncio
    async def test_list_itineraries_with_pagination(self):
        mock_db = AsyncMock(spec=AsyncSession)

        async def mock_paginate(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.items = []
            mock_result.total = 0
            return mock_result

        with patch("app.services.paginate", side_effect=mock_paginate):
            service = ItineraryService(mock_db)
            from fastapi_pagination import Params

            params = Params(page=3, size=50)
            result = await service.list_itineraries("user_id", params)


class TestItineraryUpdateValidation:
    def test_itinerary_update_end_date_before_start_date(self):
        with pytest.raises(ValidationError, match="end_date must be on or after start_date"):
            ItineraryUpdate(
                start_date=date(2024, 6, 10),
                end_date=date(2024, 6, 1),
            )

    def test_itinerary_update_end_date_after_start_date(self):
        update = ItineraryUpdate(
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 10),
        )
        assert update.end_date == date(2024, 6, 10)

    def test_itinerary_update_only_end_date(self):
        update = ItineraryUpdate(end_date=date(2024, 6, 10))
        assert update.end_date == date(2024, 6, 10)


class TestLocationUpdateValidation:
    def test_location_update_to_date_before_from_date(self):
        with pytest.raises(ValidationError, match="to_date must be on or after from_date"):
            LocationUpdate(
                from_date=date(2024, 6, 5),
                to_date=date(2024, 6, 1),
            )

    def test_location_update_to_date_after_from_date(self):
        update = LocationUpdate(
            from_date=date(2024, 6, 1),
            to_date=date(2024, 6, 10),
        )
        assert update.to_date == date(2024, 6, 10)

    def test_location_update_only_to_date(self):
        update = LocationUpdate(to_date=date(2024, 6, 10))
        assert update.to_date == date(2024, 6, 10)


class TestTransportUpdateValidation:
    def test_transport_update_arrival_before_departure(self):
        with pytest.raises(ValidationError, match="arrival_time must be after departure_time"):
            TransportUpdate(
                departure_time=datetime(2024, 6, 1, 22, 0),
                arrival_time=datetime(2024, 6, 1, 10, 0),
            )

    def test_transport_update_arrival_after_departure(self):
        update = TransportUpdate(
            departure_time=datetime(2024, 6, 1, 10, 0),
            arrival_time=datetime(2024, 6, 1, 22, 0),
        )
        assert update.arrival_time == datetime(2024, 6, 1, 22, 0)

    def test_transport_update_only_arrival_time(self):
        update = TransportUpdate(arrival_time=datetime(2024, 6, 1, 22, 0))
        assert update.arrival_time == datetime(2024, 6, 1, 22, 0)


class TestLocationServiceEdgeCases:
    @pytest.mark.asyncio
    async def test_update_location_not_found_after_ownership_check(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=None):
                service = LocationService(mock_db)
                location_data = LocationUpdate(name="Updated")

                with pytest.raises(EntityNotFoundException, match="not found"):
                    await service.update(1, location_data, "user_id")

    @pytest.mark.asyncio
    async def test_delete_location_not_found_after_ownership_check(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=None):
                service = LocationService(mock_db)

                with pytest.raises(EntityNotFoundException, match="not found"):
                    await service.delete(1, "user_id")

    @pytest.mark.asyncio
    async def test_delete_image_location_not_found_after_ownership_check(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=None):
                service = LocationService(mock_db)

                with pytest.raises(EntityNotFoundException, match="not found"):
                    await service.delete_image(1, "user_id")

    @pytest.mark.asyncio
    async def test_update_image_location_not_found_after_ownership_check(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            LocationService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=None):
                service = LocationService(mock_db)

                with pytest.raises(EntityNotFoundException, match="not found"):
                    await service.update_image(1, MagicMock(), "user_id")


class TestTransportServiceEdgeCases:
    @pytest.mark.asyncio
    async def test_update_transport_not_found_after_ownership_check(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            TransportService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=None):
                service = TransportService(mock_db)
                transport_data = TransportUpdate(carrier="Updated")

                with pytest.raises(EntityNotFoundException, match="not found"):
                    await service.update(1, transport_data, "user_id")

    @pytest.mark.asyncio
    async def test_delete_transport_not_found_after_ownership_check(self):
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(
            TransportService, "verify_ownership_and_get_itinerary", return_value=MagicMock()
        ):
            with patch.object(mock_db, "get", return_value=None):
                service = TransportService(mock_db)

                with pytest.raises(EntityNotFoundException, match="not found"):
                    await service.delete(1, "user_id")
