from datetime import datetime, timezone

from skypath.graph import build_graph
from skypath.models import Flight


# Helper to build a Flight with sensible defaults, only varying the fields a
# given test actually cares about.
def _flight(flight_number, origin, destination, departure_utc, arrival_utc):
    return Flight(
        flight_number=flight_number,
        airline="SkyPath Airways",
        origin=origin,
        destination=destination,
        departure_local=departure_utc,
        arrival_local=arrival_utc,
        departure_utc=departure_utc,
        arrival_utc=arrival_utc,
        price=100.0,
        aircraft="A320",
    )


# Flights should be indexed by their origin airport code, so the search
# algorithm can look up "what flights leave from X" in O(1).
def test_build_graph_groups_flights_by_origin_airport():
    jfk_lax = _flight(
        "SP1", "JFK", "LAX",
        datetime(2024, 3, 15, 12, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 19, tzinfo=timezone.utc),
    )
    lax_sfo = _flight(
        "SP2", "LAX", "SFO",
        datetime(2024, 3, 15, 20, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 21, tzinfo=timezone.utc),
    )

    graph = build_graph([jfk_lax, lax_sfo])

    assert graph["JFK"] == [jfk_lax]
    assert graph["LAX"] == [lax_sfo]


# Outgoing flights for an airport are pre-sorted by departure_utc, so the
# search algorithm can prune later without re-sorting on every hop.
def test_build_graph_sorts_outgoing_flights_by_departure_time():
    later = _flight(
        "SP2", "JFK", "LAX",
        datetime(2024, 3, 15, 19, tzinfo=timezone.utc),
        datetime(2024, 3, 16, 2, tzinfo=timezone.utc),
    )
    earlier = _flight(
        "SP1", "JFK", "LAX",
        datetime(2024, 3, 15, 12, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 19, tzinfo=timezone.utc),
    )

    graph = build_graph([later, earlier])

    assert graph["JFK"] == [earlier, later]


# An airport that only ever appears as a destination shouldn't produce an
# empty-list entry that callers have to special-case.
def test_build_graph_has_no_entry_for_airports_with_no_outgoing_flights():
    only_inbound = _flight(
        "SP1", "JFK", "LAX",
        datetime(2024, 3, 15, 12, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 19, tzinfo=timezone.utc),
    )

    graph = build_graph([only_inbound])

    assert "LAX" not in graph
