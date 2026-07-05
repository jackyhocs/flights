from datetime import datetime, timezone

from skypath.models import Flight, Itinerary, Layover
from skypath.serialization import serialize_response


# Helper to build a Flight with sensible defaults, only varying the fields a
# given test actually cares about.
def _flight(flight_number, origin, destination, price=100.0):
    departure = datetime(2024, 3, 15, 8, tzinfo=timezone.utc)
    arrival = datetime(2024, 3, 15, 11, tzinfo=timezone.utc)
    return Flight(
        flight_number=flight_number, airline="SkyPath Airways",
        origin=origin, destination=destination,
        origin_country="US", destination_country="US",
        departure_local=departure, arrival_local=arrival,
        departure_utc=departure, arrival_utc=arrival,
        price=price, aircraft="A320",
    )


# A response with no itineraries should still report the search parameters
# and an explicit zero count, not just an empty list with no context.
def test_serialize_response_reports_search_params_and_zero_count_when_empty():
    response = serialize_response("JFK", "LAX", "2024-03-15", [])

    assert response == {
        "origin": "JFK", "destination": "LAX", "date": "2024-03-15",
        "count": 0, "itineraries": [],
    }


# A direct itinerary's id should be just its single flight number, and its
# fields should match the documented API contract shape.
def test_serialize_response_builds_direct_itinerary_with_documented_shape():
    flight = _flight("SP101", "JFK", "LAX")
    itinerary = Itinerary(segments=[flight])

    response = serialize_response("JFK", "LAX", "2024-03-15", [itinerary])

    assert response["count"] == 1
    serialized = response["itineraries"][0]
    assert serialized["id"] == "SP101"
    assert serialized["stops"] == 0
    assert serialized["totalPrice"] == 100.0
    assert serialized["layovers"] == []
    assert serialized["segments"][0] == {
        "flightNumber": "SP101", "airline": "SkyPath Airways",
        "origin": "JFK", "destination": "LAX",
        "departureTimeLocal": "2024-03-15T08:00:00+00:00",
        "arrivalTimeLocal": "2024-03-15T11:00:00+00:00",
        "price": 100.0, "aircraft": "A320",
    }


# A multi-segment itinerary's id should join every segment's flight number,
# so the frontend has a stable-enough key without needing a real booking ID.
def test_serialize_response_joins_flight_numbers_for_connecting_itinerary_id():
    first_leg = _flight("SP1", "JFK", "ORD")
    second_leg = _flight("SP2", "ORD", "LAX")
    layover = Layover(airport="ORD", duration_minutes=60, is_domestic=True)
    itinerary = Itinerary(segments=[first_leg, second_leg], layovers=[layover])

    response = serialize_response("JFK", "LAX", "2024-03-15", [itinerary])

    serialized = response["itineraries"][0]
    assert serialized["id"] == "SP1-SP2"
    assert serialized["stops"] == 1
    assert serialized["layovers"] == [
        {"airport": "ORD", "durationMinutes": 60, "type": "domestic"},
    ]


# An international layover should be reported with type "international",
# not "domestic", so the frontend can visually distinguish the two.
def test_serialize_response_reports_international_layover_type():
    layover = Layover(airport="LHR", duration_minutes=120, is_domestic=False)
    itinerary = Itinerary(
        segments=[_flight("SP1", "JFK", "LHR"), _flight("SP2", "LHR", "CDG")],
        layovers=[layover],
    )

    response = serialize_response("JFK", "CDG", "2024-03-15", [itinerary])

    assert response["itineraries"][0]["layovers"][0]["type"] == "international"
