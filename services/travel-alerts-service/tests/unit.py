import random
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.schemas import TravelWarningCreate, TravelWarningUpdate
from app.services import (
    TravelWarningService,
    TrackedFlightService,
    FlightJobService,
    UserFlightTrackingService,
    WeatherService,
)
from core.exceptions import EntityNotFoundException, ValidationException


def random_id():
    return f"{random.randint(1000, 9999)}"


def random_flight_status():
    return random.choice(["scheduled", "in_flight", "landed", "delayed", "cancelled", "boarding"])


def random_severity():
    return random.choice(["low", "medium", "high", "critical"])


def random_category():
    return random.choice(["general", "security", "weather", "health", "transport", "political"])


def random_country_code():
    return random.choice(["US", "FR", "GB", "DE", "ES", "IT", "JP", "CA", "AU", "BR"])


def random_country_name():
    return random.choice(
        [
            "United States",
            "France",
            "Germany",
            "Spain",
            "Italy",
            "Japan",
            "Canada",
            "Australia",
            "Brazil",
            "United Kingdom",
        ]
    )


def random_datetime_future(hours=24):
    return datetime.now(timezone.utc) + timedelta(hours=random.randint(1, hours))


def random_datetime_past(hours=24):
    return datetime.now(timezone.utc) - timedelta(hours=random.randint(1, hours))


class TestTravelWarningServiceCreate:
    @pytest.mark.asyncio
    async def test_create_warning_success(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning = MagicMock()
            mock_warning.id = f"warning{random_id()}"
            mock_warning.country_code = random_country_code()
            mock_warning_class.return_value = mock_warning

            service = TravelWarningService()
            data = TravelWarningCreate(
                country_code=random_country_code(),
                country_name=random_country_name(),
                severity=random_severity(),
                title=f"Alert {random_id()}",
                description="Test description",
                category=random_category(),
                active=True,
            )

            result = await service.create(data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_create_warning_invalid_country_code(self):
        service = TravelWarningService()

        with pytest.raises(ValueError, match="must be uppercase"):
            TravelWarningCreate(
                country_code="fr",
                country_name="France",
                severity="medium",
                title="Alert",
                description="Test",
                category="test",
                active=True,
            )


class TestTravelWarningServiceRead:
    @pytest.mark.asyncio
    async def test_get_warning_success(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning = MagicMock()
            mock_warning.id = f"warning{random_id()}"
            mock_warning.country_code = random_country_code()
            mock_warning.country_name = random_country_name()
            mock_warning.region = "Paris"
            mock_warning.severity = random_severity()
            mock_warning.title = f"Alert {random_id()}"
            mock_warning.description = "Test description"
            mock_warning.category = random_category()
            mock_warning.source = "FCDO"
            mock_warning.source_url = "https://example.com"
            mock_warning.valid_from = datetime.now(timezone.utc)
            mock_warning.valid_until = datetime.now(timezone.utc) + timedelta(days=30)
            mock_warning_class.collection.get.return_value = mock_warning

            service = TravelWarningService()
            result = await service.get(f"warning{random_id()}")

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_warning_not_found(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning_class.collection.get.return_value = None

            service = TravelWarningService()
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get("warning123")

    @pytest.mark.asyncio
    async def test_get_warnings_by_country(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning_class.collection.filter.return_value.filter.return_value.order_by.return_value.fetch.return_value = []

            service = TravelWarningService()
            result = await service.get_warnings_by_country(random_country_code())

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_all_active_warnings(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning_class.collection.filter.return_value.order_by.return_value.fetch.return_value = []

            service = TravelWarningService()
            result = await service.get_all_active(0, random.randint(1, 50))

            assert isinstance(result, list)


class TestTravelWarningServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_warning_success(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning = MagicMock()
            mock_warning.id = f"warning{random_id()}"
            mock_warning.country_code = random_country_code()
            mock_warning.country_name = random_country_name()
            mock_warning.region = "Paris"
            mock_warning.severity = random_severity()
            mock_warning.title = f"Updated {random_id()}"
            mock_warning.description = "Test"
            mock_warning.category = random_category()
            mock_warning.source = "FCDO"
            mock_warning.source_url = "https://example.com"
            mock_warning.valid_from = datetime.now(timezone.utc)
            mock_warning.valid_until = datetime.now(timezone.utc) + timedelta(days=30)
            mock_warning_class.collection.get.return_value = mock_warning

            service = TravelWarningService()
            data = TravelWarningUpdate(title=f"Updated {random_id()}")
            result = await service.update(f"warning{random_id()}", data)

            assert result is not None

    @pytest.mark.asyncio
    async def test_update_warning_not_found(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning_class.collection.get.return_value = None

            service = TravelWarningService()
            data = TravelWarningUpdate(title="Updated")

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.update("warning123", data)


class TestTravelWarningServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_warning_success(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning = MagicMock()
            mock_warning.delete = Mock()
            mock_warning_class.collection.get.return_value = mock_warning

            service = TravelWarningService()
            await service.delete(f"warning{random_id()}")

            mock_warning.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_warning_not_found(self):
        with patch("app.services.TravelWarning") as mock_warning_class:
            mock_warning_class.collection.get.return_value = None

            service = TravelWarningService()

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete("warning123")


class TestTrackedFlightServiceCreate:
    @pytest.mark.asyncio
    async def test_find_or_create_flight_found(self):
        with patch("app.services.TrackedFlight") as mock_flight_class:
            departure = random_datetime_future(hours=12)
            arrival = departure + timedelta(hours=8)

            mock_existing = MagicMock()
            mock_existing.id = f"flight{random_id()}"
            mock_existing.flight_number = f"AF{random.randint(100, 999)}"
            mock_existing.airline = "Air France"
            mock_existing.departure_airport = "CDG"
            mock_existing.arrival_airport = "JFK"
            mock_existing.status = random_flight_status()
            mock_existing.scheduled_departure = departure
            mock_existing.scheduled_arrival = arrival
            mock_existing.gate = None
            mock_existing.terminal = None
            mock_existing.alert_type = None
            mock_existing.alert_message = None
            mock_flight_class.collection.filter.return_value.filter.return_value.fetch.return_value = [
                mock_existing
            ]

            service = TrackedFlightService()
            flight_data = {
                "flight_number": f"AF{random.randint(100, 999)}",
                "scheduled_departure": departure,
            }

            result = await service.find_or_create(flight_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_find_or_create_flight_new(self):
        with patch("app.services.TrackedFlight") as mock_flight_class:
            mock_flight_class.collection.filter.return_value.filter.return_value.fetch.return_value = []

            departure = random_datetime_future(hours=12)
            arrival = departure + timedelta(hours=8)

            mock_flight = MagicMock()
            mock_flight.id = f"flight{random_id()}"
            mock_flight.flight_number = f"AF{random.randint(100, 999)}"
            mock_flight.airline = "Air France"
            mock_flight.departure_airport = "CDG"
            mock_flight.arrival_airport = "JFK"
            mock_flight.status = random_flight_status()
            mock_flight.scheduled_departure = departure
            mock_flight.scheduled_arrival = arrival
            mock_flight.gate = None
            mock_flight.terminal = None
            mock_flight.alert_type = None
            mock_flight.alert_message = None
            mock_flight_class.return_value = mock_flight

            service = TrackedFlightService()
            flight_data = {
                "flight_number": f"AF{random.randint(100, 999)}",
                "scheduled_departure": departure,
                "scheduled_arrival": arrival,
            }

            result = await service.find_or_create(flight_data)
            assert result is not None


class TestFlightJobService:
    @pytest.mark.asyncio
    async def test_trigger_sync(self):
        with patch("app.services.sync_flights", return_value={"synced": random.randint(0, 100)}):
            service = FlightJobService()
            result = service.trigger_sync()

            assert result is not None

    @pytest.mark.asyncio
    async def test_lookup_flight(self):
        with patch(
            "app.services.fetch_flight_info_from_api",
            return_value={"flight_number": f"AF{random.randint(100, 999)}"},
        ):
            service = FlightJobService()
            result = await service.lookup_flight(f"AF{random.randint(100, 999)}")

            assert result is not None

    @pytest.mark.asyncio
    async def test_lookup_flight_not_found(self):
        with patch("app.services.fetch_flight_info_from_api", return_value=None):
            service = FlightJobService()
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.lookup_flight(f"AF{random.randint(100, 999)}")

    @pytest.mark.asyncio
    async def test_get_status(self):
        with patch(
            "app.services.fetch_flight_status", return_value={"status": random_flight_status()}
        ):
            service = FlightJobService()
            result = await service.get_status(f"AF{random.randint(100, 999)}", {})

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_status_not_found(self):
        with patch("app.services.fetch_flight_status", return_value=None):
            service = FlightJobService()
            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.get_status(f"AF{random.randint(100, 999)}", {})


class TestUserFlightTrackingServiceRead:
    @pytest.mark.asyncio
    async def test_get_user_trackings(self):
        with patch("app.services.UserFlightTracking") as mock_tracking_class:
            mock_tracking_class.collection.filter.return_value.filter.return_value.order_by.return_value.fetch.return_value = []

            with patch("app.services.TrackedFlight") as mock_flight_class:
                mock_flight_class.collection.get.return_value = None

                service = UserFlightTrackingService()
                result = await service.get_user_trackings(f"user{random_id()}")

                assert isinstance(result, list)


class TestUserFlightTrackingServiceCreate:
    @pytest.mark.asyncio
    async def test_create_tracking_success(self):
        with patch("app.services.UserFlightTracking") as mock_tracking_class:
            mock_tracking_class.collection.filter.return_value.filter.return_value.filter.return_value.fetch.return_value = []

            mock_tracking = MagicMock()
            mock_tracking.id = f"tracking{random_id()}"
            mock_tracking_class.return_value = mock_tracking

            departure = random_datetime_future(hours=12)
            arrival = departure + timedelta(hours=8)

            mock_flight = MagicMock()
            mock_flight.id = f"flight{random_id()}"
            mock_flight.flight_number = f"AF{random.randint(100, 999)}"
            mock_flight.airline = "Air France"
            mock_flight.departure_airport = "CDG"
            mock_flight.arrival_airport = "JFK"
            mock_flight.status = random_flight_status()
            mock_flight.scheduled_departure = departure
            mock_flight.scheduled_arrival = arrival
            mock_flight.gate = None
            mock_flight.terminal = None
            mock_flight.alert_type = None
            mock_flight.alert_message = None

            with patch.object(TrackedFlightService, "find_or_create", return_value=mock_flight):
                with patch("app.services.TrackedFlight") as mock_flight_class:
                    mock_flight_class.collection.get.return_value = mock_flight

                    service = UserFlightTrackingService()
                    flight_data = {
                        "flight_number": f"AF{random.randint(100, 999)}",
                        "departure_airport": random.choice(["CDG", "JFK", "LHR"]),
                        "arrival_airport": random.choice(["CDG", "JFK", "LHR"]),
                        "scheduled_departure": departure,
                        "scheduled_arrival": arrival,
                    }

                    result = await service.create_tracking(f"user{random_id()}", flight_data)
                    assert result is not None

    @pytest.mark.asyncio
    async def test_create_tracking_already_exists(self):
        mock_flight = MagicMock()
        mock_flight.id = f"flight{random_id()}"
        mock_flight.flight_number = f"AF{random.randint(100, 999)}"

        with patch.object(TrackedFlightService, "find_or_create", return_value=mock_flight):
            service = UserFlightTrackingService()

            with patch.object(
                service, "list", return_value=[MagicMock(id=f"existing{random_id()}")]
            ):
                flight_data = {
                    "flight_number": f"AF{random.randint(100, 999)}",
                    "scheduled_departure": random_datetime_future(),
                }

                with pytest.raises(ValidationException, match="already tracks"):
                    await service.create_tracking(f"user{random_id()}", flight_data)


class TestUserFlightTrackingServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_tracking_success(self):
        with patch("app.services.UserFlightTracking") as mock_tracking_class:
            user_id = f"user{random_id()}"
            mock_tracking = MagicMock()
            mock_tracking.id = f"tracking{random_id()}"
            mock_tracking.user_id = user_id
            mock_tracking.tracked_flight_id = f"flight{random_id()}"
            mock_tracking.active = True
            mock_tracking.created_at = datetime.now(timezone.utc)
            mock_tracking.updated_at = None
            mock_tracking.delete = Mock()
            mock_tracking_class.collection.get.return_value = mock_tracking

            service = UserFlightTrackingService()
            await service.delete_tracking(f"tracking{random_id()}", user_id)

            mock_tracking.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_tracking_not_found(self):
        with patch("app.services.UserFlightTracking") as mock_tracking_class:
            mock_tracking_class.collection.get.return_value = None

            service = UserFlightTrackingService()

            with pytest.raises(EntityNotFoundException, match="not found"):
                await service.delete_tracking(f"tracking{random_id()}", f"user{random_id()}")


class TestWeatherServiceGetByCoordinates:
    @pytest.mark.asyncio
    async def test_get_weather_by_coordinates(self):
        with patch("app.services.feature_flags") as mock_flags:
            mock_flags.ENABLE_MOCK_DATA = True

            with patch(
                "app.services.generate_mock_weather_data",
                return_value={"current": {"temp": random.randint(-10, 40)}, "daily_forecast": []},
            ):
                service = WeatherService()
                result = await service.get_weather(
                    random.uniform(-90, 90), random.uniform(-180, 180)
                )

                assert result is not None

    @pytest.mark.asyncio
    async def test_get_weather_by_coordinates_api_unavailable(self):
        with patch("app.services.feature_flags") as mock_flags:
            mock_flags.ENABLE_MOCK_DATA = False

            with patch("app.services.api_settings") as mock_settings:
                mock_settings.OPEN_METEO_AVAILABLE = "false"

                service = WeatherService()

                with pytest.raises(ValidationException):
                    await service.get_weather(random.uniform(-90, 90), random.uniform(-180, 180))


class TestWeatherServiceGetByLocation:
    @pytest.mark.asyncio
    async def test_get_weather_by_location(self):
        with patch("app.services.feature_flags") as mock_flags:
            mock_flags.ENABLE_MOCK_DATA = True

            with patch(
                "app.services.generate_mock_weather_data",
                return_value={"current": {"temp": random.randint(-10, 40)}, "daily_forecast": []},
            ):
                service = WeatherService()
                result = await service.get_weather(
                    location=random.choice(["Paris", "London", "New York", "Tokyo"])
                )

                assert result is not None


class TestGeocodingService:
    @pytest.mark.asyncio
    async def test_get_coordinates_success(self):
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [
                    {
                        "latitude": random.uniform(-90, 90),
                        "longitude": random.uniform(-180, 180),
                        "name": random.choice(["Paris", "London", "New York"]),
                        "country": random_country_name(),
                    }
                ]
            }
            mock_response.raise_for_status = Mock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            from app.services import GeocodingService

            service = GeocodingService()
            result = await service.get_coordinates(random.choice(["Paris", "London", "New York"]))

            assert result is not None


class TestFlightDataProcessor:
    def test_generate_mock_flight_update_returns_valid_data(self):
        from app.jobs.flight_data_processor import generate_mock_flight_update

        result = generate_mock_flight_update({})

        assert result is not None
        assert "status" in result
        assert "delay_minutes" in result
        assert "gate" in result
        assert "terminal" in result
        assert "alert_type" in result
        assert "alert_message" in result
        assert result["status"] in [
            "scheduled",
            "boarding",
            "in_flight",
            "landed",
            "delayed",
            "cancelled",
        ]


class TestFlightApiClient:
    def test_get_airline_name_success(self):
        from app.jobs.flight_api_client import get_airline_name

        result = get_airline_name(f"AF{random.randint(100, 999)}")
        assert result == "Air France"

    def test_get_airline_name_unknown(self):
        from app.jobs.flight_api_client import get_airline_name

        result = get_airline_name(f"ZZ{random.randint(100, 999)}")
        assert result == "ZZ"

    def test_get_airline_name_short(self):
        from app.jobs.flight_api_client import get_airline_name

        result = get_airline_name("A")
        assert result == ""

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_status_aviationstack_no_api_key(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_status_aviationstack

        mock_settings.AVIATIONSTACK_API_KEY = None
        result = fetch_flight_status_aviationstack("AF123")
        assert result is None

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_status_aviationstack_success(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_status_aviationstack

        mock_settings.AVIATIONSTACK_API_KEY = "test-key"
        mock_settings.AVIATIONSTACK_BASE_URL = "https://api.test.com"
        mock_settings.AVIATIONSTACK_TIMEOUT = 10.0

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "departure": {
                        "airport": "Paris Charles de Gaulle",
                        "iata": "CDG",
                        "scheduled": "2024-01-01T10:00:00",
                        "gate": "A42",
                        "terminal": "2E",
                    },
                    "arrival": {
                        "airport": "New York JFK",
                        "iata": "JFK",
                    },
                    "flight_status": "scheduled",
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_flight_status_aviationstack("AF123")
        assert result is not None
        assert result["status"] == "scheduled"
        assert result["gate"] == "A42"

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_status_aviationstack_cancelled(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_status_aviationstack

        mock_settings.AVIATIONSTACK_API_KEY = "test-key"
        mock_settings.AVIATIONSTACK_BASE_URL = "https://api.test.com"
        mock_settings.AVIATIONSTACK_TIMEOUT = 10.0

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "departure": {"airport": "CDG", "iata": "CDG"},
                    "arrival": {"airport": "JFK", "iata": "JFK"},
                    "flight_status": "cancelled",
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_flight_status_aviationstack("AF123")
        assert result is not None
        assert result["status"] == "cancelled"
        assert result["alert_type"] == "cancellation"

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_status_aviationstack_delayed(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_status_aviationstack

        mock_settings.AVIATIONSTACK_API_KEY = "test-key"
        mock_settings.AVIATIONSTACK_BASE_URL = "https://api.test.com"
        mock_settings.AVIATIONSTACK_TIMEOUT = 10.0

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "departure": {
                        "airport": "CDG",
                        "iata": "CDG",
                        "delay": "45",
                    },
                    "arrival": {"airport": "JFK", "iata": "JFK"},
                    "flight_status": "scheduled",
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_flight_status_aviationstack("AF123")
        assert result is not None
        assert result["status"] == "delayed"
        assert result["delay_minutes"] == 45

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_status_aviationstack_no_data(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_status_aviationstack

        mock_settings.AVIATIONSTACK_API_KEY = "test-key"
        mock_settings.AVIATIONSTACK_BASE_URL = "https://api.test.com"
        mock_settings.AVIATIONSTACK_TIMEOUT = 10.0

        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_flight_status_aviationstack("AF123")
        assert result is None

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_status_aviationstack_error(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_status_aviationstack
        import httpx

        mock_settings.AVIATIONSTACK_API_KEY = "test-key"
        mock_settings.AVIATIONSTACK_BASE_URL = "https://api.test.com"
        mock_settings.AVIATIONSTACK_TIMEOUT = 10.0

        mock_get.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock()
        )

        result = fetch_flight_status_aviationstack("AF123")
        assert result is None

    @patch("app.jobs.flight_api_client.api_settings")
    @patch("app.jobs.flight_api_client.httpx.get")
    def test_fetch_flight_info_from_api_success(self, mock_get, mock_settings):
        from app.jobs.flight_api_client import fetch_flight_info_from_api

        mock_settings.AVIATIONSTACK_API_KEY = "test-key"
        mock_settings.AVIATIONSTACK_BASE_URL = "https://api.test.com"
        mock_settings.AVIATIONSTACK_TIMEOUT = 10.0

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "departure": {
                        "airport": "Paris Charles de Gaulle",
                        "iata": "CDG",
                        "scheduled": "2024-01-01T10:00:00",
                    },
                    "arrival": {
                        "airport": "New York JFK",
                        "iata": "JFK",
                        "scheduled": "2024-01-01T14:00:00",
                    },
                    "airline": {"iata": "AF", "name": "Air France"},
                    "flight_status": "scheduled",
                    "flight_date": "2024-01-01",
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_flight_info_from_api("AF123")
        assert result is not None
        assert result["flight_number"] == "AF123"
        assert result["airline"] == "Air France"
        assert result["departure_airport_iata"] == "CDG"


class TestFcdoScraper:
    def test_determine_severity_from_html_empty(self):
        from app.jobs.fcdo_scraper import determine_severity_from_html

        result = determine_severity_from_html("")
        assert result == "low"

    def test_determine_severity_from_html_critical(self):
        from app.jobs.fcdo_scraper import determine_severity_from_html

        result = determine_severity_from_html("The FCDO advises against all travel to this country")
        assert result == "critical"

    def test_determine_severity_from_html_high(self):
        from app.jobs.fcdo_scraper import determine_severity_from_html

        result = determine_severity_from_html("Essential travel only to this region")
        assert result == "high"

    def test_determine_severity_from_html_medium(self):
        from app.jobs.fcdo_scraper import determine_severity_from_html

        result = determine_severity_from_html("Exercise caution when visiting")
        assert result == "medium"

    def test_determine_severity_summary_only(self):
        from app.jobs.fcdo_scraper import determine_severity

        result = determine_severity("Do not travel to this area")
        assert result == "critical"

    def test_determine_severity_html_takes_precedence(self):
        from app.jobs.fcdo_scraper import determine_severity

        result = determine_severity("low risk summary", "advise against all travel due to security")
        assert result == "critical"

    def test_determine_category_terrorism(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("terrorist threat in the region", "")
        assert result == "terrorism"

    def test_determine_category_political(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("civil unrest and protests", "")
        assert result == "political_unrest"

    def test_determine_category_natural_disaster(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("earthquake warning", "")
        assert result == "natural_disaster"

    def test_determine_category_health(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("disease outbreak", "")
        assert result == "health"

    def test_determine_category_crime(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("high crime rate", "")
        assert result == "crime"

    def test_determine_category_conflict(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("military conflict", "")
        assert result == "conflict"

    def test_determine_category_general(self):
        from app.jobs.fcdo_scraper import determine_category

        result = determine_category("general travel advice", "")
        assert result == "general"

    @patch("app.jobs.fcdo_scraper.httpx.get")
    def test_fetch_page_content_success(self, mock_get):
        from app.jobs.fcdo_scraper import fetch_page_content

        mock_response = MagicMock()
        mock_response.text = "<html>test content</html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_page_content("https://example.com")
        assert result == "<html>test content</html>"

    @patch("app.jobs.fcdo_scraper.httpx.get")
    def test_fetch_page_content_failure(self, mock_get):
        from app.jobs.fcdo_scraper import fetch_page_content

        mock_get.side_effect = Exception("Network error")

        result = fetch_page_content("https://example.com")
        assert result == ""

    @patch("app.jobs.fcdo_scraper.time.sleep")
    @patch("app.jobs.fcdo_scraper.fetch_page_content")
    def test_parse_fcdo_feed_success(self, mock_fetch, mock_sleep):
        from app.jobs.fcdo_scraper import parse_fcdo_feed

        mock_fetch.return_value = "<html>advises against all travel</html>"

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>France travel advice</title>
                <summary>Check latest advice before traveling</summary>
                <link href="https://www.gov.uk/foreign-travel-advice/france"/>
                <updated>2024-01-01T00:00:00Z</updated>
            </entry>
        </feed>"""

        result = parse_fcdo_feed(xml_content, lambda x: "FR")
        assert len(result) == 1
        assert result[0]["country_code"] == "FR"
        assert result[0]["severity"] == "critical"


class TestSyncWarnings:
    def test_get_country_code_exact_match(self):
        from app.jobs.sync_warnings import get_country_code

        result = get_country_code("France")
        assert result == "FR"

    def test_get_country_code_case_insensitive(self):
        from app.jobs.sync_warnings import get_country_code

        result = get_country_code("FRANCE")
        assert result == "FR"

    def test_get_country_code_partial_match(self):
        from app.jobs.sync_warnings import get_country_code

        result = get_country_code("United")
        assert result in ["US", "GB", "AE"]

    def test_get_country_code_not_found(self):
        from app.jobs.sync_warnings import get_country_code

        result = get_country_code("NonExistentCountry")
        assert result == "XX"


class TestSyncFlights:
    @patch("app.jobs.sync_flights.fetch_flight_status_aviationstack")
    @patch("app.jobs.sync_flights.generate_mock_flight_update")
    @patch("app.jobs.sync_flights.feature_flags")
    @patch("app.jobs.sync_flights.api_settings")
    @patch("app.jobs.sync_flights.config")
    def test_fetch_flight_status_mock_data(
        self, mock_config, mock_api_settings, mock_flags, mock_generate, mock_fetch
    ):
        from app.jobs.sync_flights import fetch_flight_status

        mock_config.is_prod = False
        mock_flags.ENABLE_MOCK_DATA = True
        mock_generate.return_value = {"status": "delayed", "delay_minutes": 15}

        existing = {"status": "scheduled", "delay_minutes": 0}
        result = fetch_flight_status("AF123", existing)
        assert result is not None
        assert result["status"] == "delayed"

    @patch("app.jobs.sync_flights.generate_mock_flight_update")
    @patch("app.jobs.sync_flights.feature_flags")
    @patch("app.jobs.sync_flights.api_settings")
    @patch("app.jobs.sync_flights.config")
    def test_fetch_flight_status_with_existing(
        self, mock_config, mock_api_settings, mock_flags, mock_generate
    ):
        from app.jobs.sync_flights import fetch_flight_status

        mock_config.is_prod = False
        mock_flags.ENABLE_MOCK_DATA = True
        mock_generate.return_value = {"status": "boarding", "delay_minutes": 5}

        existing = {"status": "scheduled", "delay_minutes": 0}
        result = fetch_flight_status("AF123", existing)
        assert result is not None
        assert result["status"] == "boarding"

    @patch("app.jobs.sync_flights.config")
    @patch("app.jobs.sync_flights.api_settings")
    @patch("app.jobs.sync_flights.feature_flags")
    def test_fetch_flight_status_no_api_no_existing(
        self, mock_flags, mock_api_settings, mock_config
    ):
        from app.jobs.sync_flights import fetch_flight_status

        mock_config.is_prod = True
        mock_api_settings.AVIATIONSTACK_API_KEY = None
        mock_flags.ENABLE_MOCK_DATA = False

        result = fetch_flight_status("AF123")
        assert result == {}

    def test_get_flights_to_update_empty(self):
        from app.jobs.sync_flights import get_flights_to_update
        from unittest.mock import MagicMock

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.fetch.return_value = []
        mock_db.collection.return_value = mock_collection

        result = get_flights_to_update(mock_db)
        assert result == []

    @patch("app.jobs.sync_flights.datetime")
    def test_update_flight_alert_success(self, mock_datetime):
        from app.jobs.sync_flights import update_flight_alert

        mock_now = MagicMock()
        mock_now.return_value = mock_datetime.now(timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.now.timezome.utc = timezone.utc

        mock_db = MagicMock()
        mock_flight = MagicMock()
        mock_flight.id = "flight123"
        mock_flight.status = "scheduled"
        mock_flight.delay_minutes = 0

        from app.models import TrackedFlight

        with patch.object(TrackedFlight, "collection") as mock_collection:
            mock_collection.get.return_value = mock_flight

            result = update_flight_alert(mock_db, "flight123", {"status": "delayed"})
            assert result is True

    def test_update_flight_alert_not_found(self):
        from app.jobs.sync_flights import update_flight_alert

        mock_db = MagicMock()

        from app.models import TrackedFlight

        with patch.object(TrackedFlight, "collection") as mock_collection:
            mock_collection.get.return_value = None

            result = update_flight_alert(mock_db, "nonexistent", {"status": "delayed"})
            assert result is False
