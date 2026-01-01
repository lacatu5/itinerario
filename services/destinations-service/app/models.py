from fireo.fields import BooleanField, DateTime, IDField, NumberField, TextField
from fireo.models import Model


class Destination(Model):
    class Meta:
        collection_name = "destinations"

    id = IDField()
    owner_id = TextField()
    name = TextField()
    region = TextField()
    country = TextField()
    description = TextField(default=None)
    image_url = TextField(default=None)
    latitude = TextField(default=None)
    longitude = TextField(default=None)
    address = TextField(default=None)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)


class Offer(Model):
    class Meta:
        collection_name = "offers"

    id = IDField()
    destination_id = TextField()
    title = TextField()
    description = TextField()
    accommodation_name = TextField()
    price = NumberField(default=None)
    discount_percentage = NumberField(default=None)
    valid_from = DateTime(default=None)
    valid_until = DateTime(default=None)
    image_url = TextField(default=None)
    link_url = TextField(default=None)
    active = BooleanField(default=True)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)


class Discount(Model):
    class Meta:
        collection_name = "discounts"

    id = IDField()
    destination_id = TextField()
    title = TextField()
    description = TextField()
    attraction_name = TextField()
    discount_percentage = NumberField()
    valid_from = DateTime(default=None)
    valid_until = DateTime(default=None)
    promo_code = TextField(default=None)
    link_url = TextField(default=None)
    active = BooleanField(default=True)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)


class Advertisement(Model):
    class Meta:
        collection_name = "advertisements"

    id = IDField()
    destination_id = TextField()
    title = TextField()
    description = TextField()
    event_date = DateTime(default=None)
    image_url = TextField(default=None)
    link_url = TextField(default=None)
    active = BooleanField(default=True)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)
