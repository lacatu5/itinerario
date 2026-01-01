import random
from datetime import datetime, timezone


def generate_mock_flight_update(flight_data: dict[str, object]) -> dict[str, object]:
    return {
        "status": random.choice(
            ["scheduled", "boarding", "in_flight", "landed", "delayed", "cancelled"]
        ),
        "delay_minutes": random.choice([None, 15, 30, 45, 60, 90, 120]),
        "gate": random.choice([None, "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]),
        "terminal": random.choice([None, "1", "2", "2A", "2E", "3"]),
        "actual_departure": datetime.now(timezone.utc).isoformat()
        if random.random() > 0.5
        else None,
        "actual_arrival": datetime.now(timezone.utc).isoformat() if random.random() > 0.5 else None,
        "alert_type": random.choice([None, "delay", "cancellation", "arrival", "gate_change"]),
        "alert_message": random.choice(
            [
                None,
                "Flight delayed",
                "Flight cancelled",
                "Flight has landed",
                "Gate changed",
                "Now boarding",
            ]
        ),
    }
