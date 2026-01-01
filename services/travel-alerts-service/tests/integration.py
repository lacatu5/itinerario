import random
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


def random_datetime_future(hours=24):
    return datetime.now(timezone.utc) + timedelta(hours=random.randint(1, hours))


def random_weather():
    return {
        "current": {
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180),
            "location_name": random.choice(["Paris", "London", "New York", "Tokyo"]),
            "temperature": random.randint(-10, 40),
            "feels_like": random.randint(-15, 45),
            "humidity": random.randint(0, 100),
            "wind_speed": random.randint(0, 50),
            "weather_code": random.randint(0, 100),
            "weather_description": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
            "precipitation_probability": random.randint(0, 100),
            "timestamp": datetime.now(timezone.utc),
        },
        "daily_forecast": [
            {
                "date": (datetime.now(timezone.utc) + timedelta(days=i)).strftime("%Y-%m-%d"),
                "temperature_max": random.randint(10, 35),
                "temperature_min": random.randint(-5, 25),
                "weather_code": random.randint(0, 100),
                "weather_description": random.choice(["sunny", "cloudy", "rainy"]),
                "precipitation_probability": random.randint(0, 100),
                "wind_speed_max": random.randint(0, 60),
            }
            for i in range(7)
        ],
    }


def random_warning():
    return {
        "id": f"warning_{random.randint(1000, 9999)}",
        "country_code": random.choice(["US", "FR", "GB", "DE", "ES"]),
        "country_name": random.choice(
            ["United States", "France", "Germany", "Spain", "United Kingdom"]
        ),
        "severity": random.choice(["low", "medium", "high"]),
        "title": f"Warning {random.randint(1, 100)}",
        "description": "Test warning description",
        "category": random.choice(["general", "security", "weather", "health"]),
    }


class TestRouterIntegration:
    @pytest.mark.asyncio
    async def test_get_weather_by_location(self):
        from core.auth.firebase import get_current_user_id

        app.dependency_overrides[get_current_user_id] = lambda: "test_user"

        async def mock_weather(*args, **kwargs):
            return random_weather()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.WeatherService.get_weather", side_effect=mock_weather):
                response = await ac.get("/api/travel-alerts/weather?location=Paris")

        app.dependency_overrides.clear()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_weather_by_coordinates(self):
        from core.auth.firebase import get_current_user_id

        app.dependency_overrides[get_current_user_id] = lambda: "test_user"

        async def mock_weather(*args, **kwargs):
            return random_weather()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.WeatherService.get_weather", side_effect=mock_weather):
                response = await ac.get(
                    "/api/travel-alerts/weather?latitude=48.8566&longitude=2.3522"
                )

        app.dependency_overrides.clear()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_weather_no_params(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/travel-alerts/weather")

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_warning_by_id_not_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/travel-alerts/warnings/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_warning(self):
        from core.auth.firebase import get_current_user_id

        app.dependency_overrides[get_current_user_id] = lambda: "test_user"

        warning_data = random_warning()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/travel-alerts/warnings", json=warning_data)

        app.dependency_overrides.clear()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_warning_not_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.put(
                "/api/travel-alerts/warnings/nonexistent", json={"title": "Updated"}
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_warning_not_found(self):
        with patch("app.services.TravelWarning") as mock_class:
            mock_class.collection.get.return_value = None

            from core.auth.firebase import get_current_user_id

            app.dependency_overrides[get_current_user_id] = lambda: "test_user"

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.delete("/api/travel-alerts/warnings/nonexistent")

            app.dependency_overrides.clear()
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_my_flights(self):
        from core.auth.firebase import get_current_user_id

        app.dependency_overrides[get_current_user_id] = lambda: "test_user"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.UserFlightTracking") as mock_tracking:
                mock_tracking.collection.filter.return_value.filter.return_value.fetch.return_value = []
                response = await ac.get("/api/travel-alerts/flights")

        app.dependency_overrides.clear()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_warnings_by_country(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.TravelWarning") as mock_warning:
                mock_warning.collection.filter.return_value.filter.return_value.order_by.return_value.fetch.return_value = []

                country_code = random.choice(["US", "FR", "GB", "DE", "ES"])
                response = await ac.get(f"/api/travel-alerts/warnings?country_code={country_code}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_all_warnings_without_country(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.TravelWarning") as mock_warning:
                mock_warning.collection.filter.return_value.order_by.return_value.fetch.return_value = []

                response = await ac.get("/api/travel-alerts/warnings?skip=0&limit=10")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lookup_flight_by_number_success(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.fetch_flight_info_from_api") as mock_fetch:
                mock_fetch.return_value = {
                    "flight_number": f"AF{random.randint(100, 999)}",
                    "status": "scheduled",
                    "airline": "Air France",
                }

                flight_number = f"AF{random.randint(100, 999)}"
                response = await ac.get(f"/api/travel-alerts/flights/lookup/{flight_number}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_flight_tracking(self):
        from core.auth.firebase import get_current_user_id

        app.dependency_overrides[get_current_user_id] = lambda: "test_user"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.UserFlightTracking") as mock_tracking:
                mock_tracking.collection.get.return_value = None
                response = await ac.delete("/api/travel-alerts/flights/some_tracking_id")

        app.dependency_overrides.clear()
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_trigger_flight_sync(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch(
                "app.services.sync_flights",
                return_value={"success": True, "updated": random.randint(0, 100)},
            ):
                response = await ac.post("/api/travel-alerts/flights/sync")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lookup_flight_not_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch("app.services.fetch_flight_info_from_api", return_value=None):
                response = await ac.get("/api/travel-alerts/flights/lookup/XX9999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_flight_status_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            with patch(
                "app.services.fetch_flight_status",
                return_value={"status": random.choice(["scheduled", "delayed", "cancelled"])},
            ):
                response = await ac.get("/api/travel-alerts/flights/AF123/status")

        assert response.status_code == 200
