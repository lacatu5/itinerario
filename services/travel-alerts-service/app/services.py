import random
from datetime import datetime, timedelta, timezone

import httpx
from loguru import logger

from app.jobs.sync_flights import (
    fetch_flight_info_from_api,
    fetch_flight_status,
    sync_flights,
)
from app.models import TrackedFlight, TravelWarning, UserFlightTracking
from app.schemas import (
    TrackedFlightResponse as TrackedFlightSchema,
)
from app.schemas import (
    TravelWarningCreate,
    TravelWarningResponse,
    TravelWarningUpdate,
)
from app.utils.constants import WEATHER_CODES
from core.auth.ownership import verify_ownership
from core.config import api_settings, feature_flags
from core.exceptions import EntityNotFoundException, ValidationException
from core.firestore.models import BaseFirestoreService


class TravelWarningService(BaseFirestoreService):
    def __init__(self):
        super().__init__(TravelWarning, TravelWarningResponse)

    async def get(self, warning_id: str) -> TravelWarningResponse:
        warning = TravelWarning.collection.get(warning_id)
        if not warning:
            raise EntityNotFoundException(f"TravelWarning {warning_id} not found")
        return TravelWarningResponse.model_validate(warning)

    async def create(self, data: TravelWarningCreate) -> TravelWarningResponse:
        warning = TravelWarning()
        for key, value in data.model_dump().items():
            setattr(warning, key, value)
        warning.save()
        logger.info(f"Travel warning created: {warning.country_code} - {warning.title}")
        return TravelWarningResponse.model_validate(warning)

    async def update(self, warning_id: str, data: TravelWarningUpdate) -> TravelWarningResponse:
        warning = TravelWarning.collection.get(warning_id)
        if not warning:
            raise EntityNotFoundException(f"TravelWarning {warning_id} not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(warning, key, value)
        warning.save()
        logger.info(f"Travel warning {warning_id} updated")
        return TravelWarningResponse.model_validate(warning)

    async def delete(self, warning_id: str) -> None:
        warning = TravelWarning.collection.get(warning_id)
        if not warning:
            raise EntityNotFoundException(f"TravelWarning {warning_id} not found")
        warning.delete()
        logger.info(f"Travel warning {warning_id} deleted")

    async def get_warnings_by_country(self, country_code: str, active_only: bool = True):
        filters = {"country_code": {"op": "==", "value": country_code.upper()}}
        if active_only:
            filters["active"] = {"op": "==", "value": True}
        warnings = self.list(filters=filters, order_by="-created_at")
        logger.info(f"Retrieved {len(warnings)} travel warnings for country {country_code.upper()}")
        return warnings

    async def get_all_active(self, skip: int = 0, limit: int = 50):
        filters = {"active": {"op": "==", "value": True}}
        all_warnings = self.list(filters=filters, order_by="-created_at", limit=limit, skip=skip)
        return all_warnings


class TrackedFlightService(BaseFirestoreService):
    def __init__(self):
        super().__init__(TrackedFlight, TrackedFlightSchema)

    async def find_or_create(self, flight_data: dict[str, object]) -> TrackedFlightSchema:
        flight_number = flight_data["flight_number"]
        scheduled_departure = flight_data["scheduled_departure"]

        filters = {
            "flight_number": {"op": "==", "value": flight_number},
            "scheduled_departure": {"op": "==", "value": scheduled_departure},
        }
        existing = self.list(filters=filters)

        if existing:
            logger.info(f"Found existing tracked flight {flight_number}")
            return existing[0]

        tracked_flight = TrackedFlight()
        for key, value in flight_data.items():
            setattr(tracked_flight, key, value)
        tracked_flight.save()
        logger.info(f"Created tracked flight {flight_number}")
        return TrackedFlightSchema.model_validate(tracked_flight)


class FlightJobService:
    async def trigger_sync(self) -> dict[str, object]:
        return sync_flights()

    async def lookup_flight(self, flight_number: str) -> dict[str, object]:
        result = fetch_flight_info_from_api(flight_number)
        if not result:
            raise EntityNotFoundException(f"Flight {flight_number} not found")
        return result

    async def get_status(
        self, flight_number: str, flight_data: dict[str, object]
    ) -> dict[str, object]:
        result = fetch_flight_status(flight_number, flight_data)
        if not result:
            raise EntityNotFoundException(f"Flight {flight_number} not found")
        return result


class UserFlightTrackingService(BaseFirestoreService):
    def __init__(self):
        super().__init__(UserFlightTracking, TrackedFlightSchema)

    async def get_user_trackings(self, user_id: str) -> list[dict[str, object]]:
        filters = {
            "user_id": {"op": "==", "value": user_id},
            "active": {"op": "==", "value": True},
        }
        results = self.list(filters=filters, order_by="-created_at")

        trackings = []
        for tracking in results:
            flight = TrackedFlight.collection.get(tracking.tracked_flight_id)
            if flight:
                trackings.append(
                    {
                        "id": tracking.id,
                        "user_id": tracking.user_id,
                        "tracked_flight_id": tracking.tracked_flight_id,
                        "flight": TrackedFlightSchema.model_validate(flight).model_dump(),
                        "active": tracking.active,
                        "created_at": tracking.created_at,
                        "updated_at": tracking.updated_at,
                    }
                )

        logger.info(f"Retrieved {len(trackings)} flight trackings for user {user_id}")
        return trackings

    async def create_tracking(
        self, user_id: str, flight_data: dict[str, object]
    ) -> dict[str, object]:
        tracked_flight_service = TrackedFlightService()

        tracked_flight = await tracked_flight_service.find_or_create(flight_data)

        filters = {
            "user_id": {"op": "==", "value": user_id},
            "tracked_flight_id": {"op": "==", "value": tracked_flight.id},
            "active": {"op": "==", "value": True},
        }
        existing = self.list(filters=filters)

        if existing:
            raise ValidationException("User already tracks this flight")

        tracking = UserFlightTracking()
        tracking.user_id = user_id
        tracking.tracked_flight_id = tracked_flight.id
        tracking.active = True
        tracking.save()

        flight = TrackedFlight.collection.get(tracked_flight.id)

        logger.info(
            f"Flight tracking created for user {user_id}, flight {tracked_flight.flight_number}"
        )
        return {
            "id": tracking.id,
            "user_id": tracking.user_id,
            "tracked_flight_id": tracking.tracked_flight_id,
            "flight": TrackedFlightSchema.model_validate(flight).model_dump(),
            "active": tracking.active,
            "created_at": tracking.created_at,
        }

    async def delete_tracking(self, tracking_id: str, user_id: str) -> None:
        tracking = UserFlightTracking.collection.get(tracking_id)
        if not tracking:
            raise EntityNotFoundException(f"Tracking {tracking_id} not found")
        verify_ownership(tracking.user_id, user_id, "tracking")
        tracking.delete()
        logger.info(f"Flight tracking {tracking_id} deleted by user {user_id}")


class GeocodingService:
    def __init__(self):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1"

    async def get_coordinates(self, location_name: str) -> dict[str, object]:
        logger.info(f"Geocoding location: {location_name}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.geocoding_url}/search",
                    params={
                        "name": location_name,
                        "count": 1,
                        "language": "en",
                        "format": "json",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                if data.get("results"):
                    result = data["results"][0]
                    logger.info(
                        f"Geocoded {location_name} to ({result['latitude']}, {result['longitude']})"
                    )
                    return {
                        "latitude": result["latitude"],
                        "longitude": result["longitude"],
                        "name": result.get("name"),
                        "country": result.get("country"),
                    }
                raise ValidationException(f"Location not found: {location_name}")
        except Exception as e:
            logger.opt(exception=True).error(f"Geocoding failed for {location_name}: {e}")
            raise ValidationException(
                f"Geocoding service unavailable for location: {location_name}"
            )


def generate_mock_weather_data(
    latitude: float, longitude: float, location_name: str | None = None
) -> dict[str, object]:
    return {
        "current": {
            "latitude": latitude,
            "longitude": longitude,
            "location_name": location_name,
            "temperature": random.randint(-10, 40),
            "feels_like": random.randint(-15, 45),
            "humidity": random.randint(0, 100),
            "wind_speed": random.randint(0, 50),
            "weather_code": random.randint(0, 100),
            "weather_description": random.choice(list(WEATHER_CODES.values())),
            "precipitation_probability": random.randint(0, 100),
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
        },
        "daily_forecast": [
            {
                "date": (datetime.now(timezone.utc) + timedelta(days=i)).strftime("%Y-%m-%d"),
                "temperature_max": random.randint(10, 35),
                "temperature_min": random.randint(-5, 25),
                "weather_code": random.randint(0, 100),
                "weather_description": random.choice(list(WEATHER_CODES.values())),
                "precipitation_probability": random.randint(0, 100),
                "wind_speed_max": random.randint(0, 60),
            }
            for i in range(7)
        ],
    }


class WeatherService:
    def __init__(self):
        self.geocoding_service = GeocodingService()

    async def get_weather(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        location: str | None = None,
    ) -> dict[str, object]:
        if location:
            return await self._get_weather_by_location(location)
        elif latitude is not None and longitude is not None:
            return await self._get_weather_by_coordinates(latitude, longitude)
        else:
            raise ValidationException("Provide either location name or latitude/longitude")

    async def _get_weather_by_coordinates(
        self, latitude: float, longitude: float, location_name: str | None = None
    ) -> dict[str, object]:
        logger.info(f"Fetching weather data for coordinates ({latitude}, {longitude})")
        if feature_flags.ENABLE_MOCK_DATA:
            return generate_mock_weather_data(latitude, longitude, location_name)

        if api_settings.OPEN_METEO_AVAILABLE.lower() != "true":
            raise ValidationException(
                f"Weather service unavailable for coordinates ({latitude}, {longitude})"
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_weather": "true",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                    "timezone": "auto",
                    "forecast_days": "7",
                }
                response = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            current = data.get("current_weather", {})
            daily = data.get("daily", {})

            weather_code = current.get("weathercode", 0)

            current_weather = {
                "latitude": latitude,
                "longitude": longitude,
                "location_name": location_name,
                "temperature": current.get("temperature", 0),
                "feels_like": current.get("apparent_temperature", 0),
                "humidity": current.get("relativehumidity_2m", 0),
                "wind_speed": current.get("windspeed_10m", 0),
                "weather_code": weather_code,
                "weather_description": WEATHER_CODES.get(weather_code, "Unknown"),
                "precipitation_probability": None,
                "timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            }

            daily_forecast = []
            daily_time = daily.get("time", [])
            if daily_time:
                for i in range(len(daily_time)):
                    weather_codes = daily.get("weather_code", [])
                    temp_max = daily.get("temperature_2m_max", [])
                    temp_min = daily.get("temperature_2m_min", [])
                    precip = daily.get("precipitation_probability_max", [])
                    wind = daily.get("wind_speed_10m_max", [])

                    code = weather_codes[i] if i < len(weather_codes) else 0

                    daily_forecast.append(
                        {
                            "date": daily_time[i],
                            "temperature_max": temp_max[i] if i < len(temp_max) else 0,
                            "temperature_min": temp_min[i] if i < len(temp_min) else 0,
                            "weather_code": code,
                            "weather_description": WEATHER_CODES.get(code, "Unknown"),
                            "precipitation_probability": precip[i] if i < len(precip) else 0,
                            "wind_speed_max": wind[i] if i < len(wind) else 0,
                        }
                    )

            logger.info(f"Weather data fetched successfully for {location_name or 'coordinates'}")
            return {"current": current_weather, "daily_forecast": daily_forecast}
        except Exception as e:
            logger.opt(exception=True).error(f"Failed to fetch weather data: {e}")
            raise ValidationException(
                f"Failed to fetch weather data for {location_name or f'coordinates ({latitude}, {longitude})'}"
            )

    async def _get_weather_by_location(self, location_name: str) -> dict[str, object]:
        logger.info(f"Fetching weather data for location: {location_name}")
        if feature_flags.ENABLE_MOCK_DATA:
            mock_lat = random.uniform(40.0, 60.0)
            mock_lon = random.uniform(-10.0, 10.0)
            return generate_mock_weather_data(mock_lat, mock_lon, location_name)

        coords = await self.geocoding_service.get_coordinates(location_name)
        return await self._get_weather_by_coordinates(
            coords["latitude"],
            coords["longitude"],
            f"{coords['name']}, {coords['country']}",
        )
