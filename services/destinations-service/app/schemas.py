from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class DestinationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    region: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    address: str | None = None


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    region: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    address: str | None = None


class DestinationResponse(DestinationBase):
    id: str = ""
    owner_id: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DestinationWithContent(DestinationResponse):
    advertisements: list["AdvertisementResponse"] = Field(default_factory=list)
    offers: list["OfferResponse"] = Field(default_factory=list)
    discounts: list["DiscountResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DestinationsListResponse(BaseModel):
    items: list[DestinationResponse]
    next_cursor: str | None = None
    has_more: bool = False


class AdvertisementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    event_date: datetime | None = None
    image_url: str | None = None
    link_url: str | None = None
    active: bool


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    event_date: datetime | None = None
    image_url: str | None = None
    link_url: str | None = None
    active: bool | None = None


class AdvertisementResponse(AdvertisementBase):
    id: str = ""
    destination_id: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AdvertisementsListResponse(BaseModel):
    items: list[AdvertisementResponse]
    next_cursor: str | None = None
    has_more: bool = False


class DiscountBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    attraction_name: str = Field(..., min_length=1, max_length=200)
    discount_percentage: int = Field(..., ge=0, le=100)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    promo_code: str | None = None
    link_url: str | None = None
    active: bool


class DiscountCreate(DiscountBase):
    @field_validator("valid_until")
    @classmethod
    def valid_until_after_valid_from(
        cls, v: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        if v is not None and info.data.get("valid_from") is not None:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class DiscountUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    attraction_name: str | None = Field(default=None, min_length=1, max_length=200)
    discount_percentage: int | None = Field(default=None, ge=0, le=100)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    promo_code: str | None = None
    link_url: str | None = None
    active: bool | None = None

    @field_validator("valid_until")
    @classmethod
    def valid_until_after_valid_from(
        cls, v: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        if v is not None and info.data.get("valid_from") is not None:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class DiscountResponse(DiscountBase):
    id: str = ""
    destination_id: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DiscountsListResponse(BaseModel):
    items: list[DiscountResponse]
    next_cursor: str | None = None
    has_more: bool = False


class OfferBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    accommodation_name: str = Field(..., min_length=1, max_length=200)
    price: float | None = Field(default=None, ge=0)
    discount_percentage: int | None = Field(default=None, ge=0, le=100)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    image_url: str | None = None
    link_url: str | None = None
    active: bool


class OfferCreate(OfferBase):
    @field_validator("valid_until")
    @classmethod
    def valid_until_after_valid_from(
        cls, v: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        if v is not None and info.data.get("valid_from") is not None:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class OfferUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    accommodation_name: str | None = Field(default=None, min_length=1, max_length=200)
    price: float | None = Field(default=None, ge=0)
    discount_percentage: int | None = Field(default=None, ge=0, le=100)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    image_url: str | None = None
    link_url: str | None = None
    active: bool | None = None

    @field_validator("valid_until")
    @classmethod
    def valid_until_after_valid_from(
        cls, v: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        if v is not None and info.data.get("valid_from") is not None:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class OfferResponse(OfferBase):
    id: str = ""
    destination_id: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OffersListResponse(BaseModel):
    items: list[OfferResponse]
    next_cursor: str | None = None
    has_more: bool = False
