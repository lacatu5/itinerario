from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class WeatherData(BaseModel):
    latitude: float
    longitude: float
    location_name: str | None = None
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    weather_code: int
    weather_description: str
    precipitation_probability: int | None = None
    timestamp: datetime


class WeatherForecast(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    weather_code: int
    weather_description: str
    precipitation_probability: int
    wind_speed_max: float


class WeatherResponse(BaseModel):
    current: WeatherData
    daily_forecast: list[WeatherForecast]


class TravelWarningBase(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str
    region: str | None = None
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    title: str
    description: str
    category: str
    source: str | None = None
    source_url: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    active: bool = True

    @field_validator("country_code")
    @classmethod
    def country_code_uppercase(cls, v: str) -> str:
        if not v.isupper():
            raise ValueError("country_code must be uppercase")
        return v

    @field_validator("valid_until")
    @classmethod
    def valid_from_before_until(cls, v: datetime | None, info: ValidationInfo) -> datetime | None:
        if v is not None and info.data.get("valid_from") is not None:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class TravelWarningCreate(TravelWarningBase):
    pass


class TravelWarningUpdate(BaseModel):
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    country_name: str | None = Field(default=None, min_length=1, max_length=200)
    region: str | None = None
    severity: str | None = Field(default=None, pattern="^(low|medium|high|critical)$")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    source: str | None = None
    source_url: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    active: bool | None = None

    @field_validator("valid_until")
    @classmethod
    def valid_from_before_until(cls, v: datetime | None, info: ValidationInfo) -> datetime | None:
        if v is not None and info.data.get("valid_from") is not None:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class TravelWarningResponse(TravelWarningBase):
    id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TravelWarningsListResponse(BaseModel):
    warnings: list[TravelWarningResponse]
    total_count: int


class TrackedFlightBase(BaseModel):
    flight_number: str
    airline: str | None = None
    departure_airport: str
    arrival_airport: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    actual_departure: datetime | None = None
    actual_arrival: datetime | None = None
    status: str
    delay_minutes: int | None = None
    gate: str | None = None
    terminal: str | None = None
    alert_type: str | None = None
    alert_message: str | None = None

    @field_validator("scheduled_arrival")
    @classmethod
    def scheduled_arrival_after_departure(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "scheduled_departure" in info.data and v < info.data["scheduled_departure"]:
            raise ValueError("scheduled_arrival must be after scheduled_departure")
        return v


class TrackedFlightResponse(TrackedFlightBase):
    id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TrackedFlightsListResponse(BaseModel):
    flights: list[TrackedFlightResponse]
    total_count: int


class UserFlightTrackingBase(BaseModel):
    tracked_flight_id: str
    active: bool = True


class UserFlightTrackingCreate(BaseModel):
    flight_number: str
    airline: str | None = None
    departure_airport: str
    arrival_airport: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    status: str = "scheduled"

    @field_validator("scheduled_arrival")
    @classmethod
    def scheduled_arrival_after_departure(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "scheduled_departure" in info.data and v < info.data["scheduled_departure"]:
            raise ValueError("scheduled_arrival must be after scheduled_departure")
        return v


class UserFlightTracking(UserFlightTrackingBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserFlightTrackingWithFlight(BaseModel):
    id: str
    user_id: str
    tracked_flight_id: str
    flight: TrackedFlightResponse
    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserFlightTrackingsListResponse(BaseModel):
    trackings: list[UserFlightTrackingWithFlight]
    total_count: int


class FlightSyncResponse(BaseModel):
    message: str
    result: dict[str, object]


class FlightInfoResponse(BaseModel):
    flight_number: str
    status: dict[str, object]
