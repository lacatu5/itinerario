from fastapi import APIRouter, Depends, Query

from app.schemas import (
    FlightInfoResponse,
    FlightSyncResponse,
    TravelWarningCreate,
    TravelWarningResponse,
    TravelWarningsListResponse,
    TravelWarningUpdate,
    UserFlightTrackingCreate,
    UserFlightTrackingsListResponse,
    UserFlightTrackingWithFlight,
    WeatherResponse,
)
from app.services import (
    FlightJobService,
    TravelWarningService,
    UserFlightTrackingService,
    WeatherService,
)
from core.auth.firebase import get_current_user_id


def get_weather_service() -> WeatherService:
    return WeatherService()


def get_travel_warning_service() -> TravelWarningService:
    return TravelWarningService()


def get_user_flight_tracking_service() -> UserFlightTrackingService:
    return UserFlightTrackingService()


def get_flight_job_service() -> FlightJobService:
    return FlightJobService()


api_router = APIRouter(prefix="/api/travel-alerts", tags=["Travel Alerts"])


@api_router.get("/weather", response_model=WeatherResponse, summary="Get weather information")
async def get_weather(
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    location: str | None = Query(None),
    service: WeatherService = Depends(get_weather_service),
):
    result = await service.get_weather(latitude, longitude, location)
    return WeatherResponse(**result)


@api_router.get(
    "/warnings", response_model=TravelWarningsListResponse, summary="Get travel warnings"
)
async def get_travel_warnings(
    country_code: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: TravelWarningService = Depends(get_travel_warning_service),
):
    if country_code:
        warnings = await service.get_warnings_by_country(country_code)
    else:
        warnings = await service.get_all_active(skip=skip, limit=limit)
    return TravelWarningsListResponse(
        warnings=warnings,
        total_count=len(warnings),
    )


@api_router.get(
    "/warnings/{warning_id}",
    response_model=TravelWarningResponse,
    summary="Get travel warning by ID",
)
async def get_travel_warning(
    warning_id: str,
    service: TravelWarningService = Depends(get_travel_warning_service),
):
    return await service.get(warning_id)


@api_router.post("/warnings", response_model=TravelWarningResponse, summary="Create travel warning")
async def create_travel_warning(
    warning: TravelWarningCreate,
    service: TravelWarningService = Depends(get_travel_warning_service),
):
    return await service.create(warning)


@api_router.put(
    "/warnings/{warning_id}", response_model=TravelWarningResponse, summary="Update travel warning"
)
async def update_travel_warning(
    warning_id: str,
    warning: TravelWarningUpdate,
    service: TravelWarningService = Depends(get_travel_warning_service),
):
    return await service.update(warning_id, warning)


@api_router.delete("/warnings/{warning_id}", status_code=204, summary="Delete travel warning")
async def delete_travel_warning(
    warning_id: str,
    service: TravelWarningService = Depends(get_travel_warning_service),
) -> None:
    await service.delete(warning_id)


@api_router.get(
    "/flights", response_model=UserFlightTrackingsListResponse, summary="Get my flight trackings"
)
async def get_my_flight_trackings(
    user_id: str = Depends(get_current_user_id),
    service: UserFlightTrackingService = Depends(get_user_flight_tracking_service),
):
    trackings = await service.get_user_trackings(user_id)
    return UserFlightTrackingsListResponse(trackings=trackings, total_count=len(trackings))


@api_router.post(
    "/flights", response_model=UserFlightTrackingWithFlight, summary="Create flight tracking"
)
async def create_flight_tracking(
    tracking: UserFlightTrackingCreate,
    user_id: str = Depends(get_current_user_id),
    service: UserFlightTrackingService = Depends(get_user_flight_tracking_service),
):
    flight_data = tracking.model_dump()
    return await service.create_tracking(user_id, flight_data)


@api_router.delete("/flights/{tracking_id}", status_code=204, summary="Delete flight tracking")
async def delete_flight_tracking(
    tracking_id: str,
    user_id: str = Depends(get_current_user_id),
    service: UserFlightTrackingService = Depends(get_user_flight_tracking_service),
) -> None:
    await service.delete_tracking(tracking_id, user_id)


@api_router.post("/flights/sync", response_model=FlightSyncResponse, summary="Trigger flight sync")
async def trigger_flight_sync(service: FlightJobService = Depends(get_flight_job_service)):
    result = await service.trigger_sync()
    return FlightSyncResponse(message="Flight sync completed", result=result)


@api_router.get(
    "/flights/lookup/{flight_number}",
    response_model=FlightInfoResponse,
    summary="Lookup flight information",
)
async def lookup_flight_info(
    flight_number: str,
    service: FlightJobService = Depends(get_flight_job_service),
):
    flight_info = await service.lookup_flight(flight_number)
    return FlightInfoResponse(flight_number=flight_number, status=flight_info)


@api_router.get(
    "/flights/{flight_number}/status",
    response_model=FlightInfoResponse,
    summary="Get flight status",
)
async def get_flight_status(
    flight_number: str,
    service: FlightJobService = Depends(get_flight_job_service),
):
    status = await service.get_status(
        flight_number,
        {
            "flight_number": flight_number,
            "status": "scheduled",
            "scheduled_departure": None,
        },
    )
    return FlightInfoResponse(flight_number=flight_number, status=status)
