from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItineraryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date | None = None
    short_description: str = Field(..., min_length=1, max_length=80)
    detail_description: str | None = Field(default=None, max_length=5000)
    image_url: str | None = Field(default=None, max_length=500)
    latitude: str | None = Field(default=None, max_length=50)
    longitude: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=500)


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    short_description: str = Field(..., min_length=1, max_length=500)
    from_date: date
    to_date: date
    image_url: str | None = Field(default=None, max_length=500)
    latitude: str | None = Field(default=None, max_length=50)
    longitude: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=500)


class TransportBase(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    departure_location: str = Field(..., min_length=1, max_length=200)
    arrival_location: str = Field(..., min_length=1, max_length=200)
    departure_time: datetime
    arrival_time: datetime
    carrier: str | None = Field(default=None, max_length=100)
    transport_number: str | None = Field(default=None, max_length=50)


class ItineraryCreate(ItineraryBase):
    pass

    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v: date | None, info) -> date | None:
        if v is not None and "start_date" in info.data:
            if v < info.data["start_date"]:
                raise ValueError("end_date must be on or after start_date")
        return v


class ItineraryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    destination: str | None = Field(default=None, min_length=1, max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    short_description: str | None = Field(default=None, min_length=1, max_length=80)
    detail_description: str | None = Field(default=None)
    image_url: str | None = Field(default=None, max_length=500)
    latitude: str | None = Field(default=None, max_length=50)
    longitude: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=500)

    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v: date | None, info) -> date | None:
        if v is not None and "start_date" in info.data and info.data["start_date"] is not None:
            if v < info.data["start_date"]:
                raise ValueError("end_date must be on or after start_date")
        return v


class LocationCreate(LocationBase):
    pass

    @field_validator("to_date")
    @classmethod
    def to_date_after_from_date(cls, v: date, info) -> date:
        if "from_date" in info.data and v < info.data["from_date"]:
            raise ValueError("to_date must be on or after from_date")
        return v


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    short_description: str | None = Field(default=None, min_length=1, max_length=500)
    from_date: date | None = None
    to_date: date | None = None
    latitude: str | None = Field(default=None, max_length=50)
    longitude: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=500)

    @field_validator("to_date")
    @classmethod
    def to_date_after_from_date(cls, v: date | None, info) -> date | None:
        if v is not None and "from_date" in info.data and info.data["from_date"] is not None:
            if v < info.data["from_date"]:
                raise ValueError("to_date must be on or after from_date")
        return v


class TransportCreate(TransportBase):
    pass

    @field_validator("arrival_time")
    @classmethod
    def arrival_after_departure(cls, v: datetime, info) -> datetime:
        if "departure_time" in info.data and v < info.data["departure_time"]:
            raise ValueError("arrival_time must be after departure_time")
        return v


class TransportUpdate(BaseModel):
    type: str | None = Field(default=None, min_length=1, max_length=50)
    departure_location: str | None = Field(default=None, min_length=1, max_length=200)
    arrival_location: str | None = Field(default=None, min_length=1, max_length=200)
    departure_time: datetime | None = None
    arrival_time: datetime | None = None
    carrier: str | None = Field(default=None, max_length=100)
    transport_number: str | None = Field(default=None, max_length=50)

    @field_validator("arrival_time")
    @classmethod
    def arrival_after_departure(cls, v: datetime | None, info) -> datetime | None:
        if (
            v is not None
            and "departure_time" in info.data
            and info.data["departure_time"] is not None
        ):
            if v < info.data["departure_time"]:
                raise ValueError("arrival_time must be after departure_time")
        return v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str | None = None
    profile_image_url: str | None = None
    created_at: datetime


class ItineraryResponse(ItineraryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime


class ItineraryWithOwnerResponse(ItineraryResponse):
    owner: UserResponse


class ItinerarySearchRequest(BaseModel):
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    search_text: str | None = None
    skip: int = 0
    limit: int = 100


class ItinerarySearchResult(BaseModel):
    results: list[ItineraryWithOwnerResponse] = Field(
        ..., description="List of itineraries with owner info"
    )
    total: int = Field(..., ge=0, description="Total number of results")

    model_config = ConfigDict(from_attributes=True)


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    itinerary_id: int
    created_at: datetime


class TransportResponse(TransportBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    itinerary_id: int
    created_at: datetime
