from fireo.fields import BooleanField, DateTime, IDField, NumberField, TextField
from fireo.models import Model


class TrackedFlight(Model):
    class Meta:
        collection_name = "tracked_flights"

    id = IDField()
    flight_number = TextField()
    airline = TextField(default=None)
    departure_airport = TextField()
    arrival_airport = TextField()
    scheduled_departure = DateTime()
    scheduled_arrival = DateTime()
    actual_departure = DateTime(default=None)
    actual_arrival = DateTime(default=None)
    status = TextField()
    delay_minutes = NumberField(default=None)
    gate = TextField(default=None)
    terminal = TextField(default=None)
    alert_type = TextField(default=None)
    alert_message = TextField(default=None)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)


class UserFlightTracking(Model):
    class Meta:
        collection_name = "user_flight_tracking"

    id = IDField()
    user_id = TextField()
    tracked_flight_id = TextField()
    active = BooleanField(default=True)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)


class TravelWarning(Model):
    class Meta:
        collection_name = "travel_warnings"

    id = IDField()
    country_code = TextField()
    country_name = TextField()
    region = TextField(default=None)
    severity = TextField()
    title = TextField()
    description = TextField()
    category = TextField()
    source = TextField(default=None)
    source_url = TextField(default=None)
    valid_from = DateTime(default=None)
    valid_until = DateTime(default=None)
    active = BooleanField(default=True)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)
