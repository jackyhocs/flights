import json
import logging

import pytest

from skypath.data_loader import load_dataset
from skypath.time_utils import to_utc

DEFAULT_AIRPORTS = [
    {"code": "JFK", "name": "JFK", "city": "New York", "country": "US",
     "timezone": "America/New_York"},
    {"code": "LAX", "name": "LAX", "city": "Los Angeles", "country": "US",
     "timezone": "America/Los_Angeles"},
]

DEFAULT_FLIGHT = {
    "flightNumber": "SP101",
    "airline": "SkyPath Airways",
    "origin": "JFK",
    "destination": "LAX",
    "departureTime": "2024-03-15T08:30:00",
    "arrivalTime": "2024-03-15T11:45:00",
    "price": 299.0,
    "aircraft": "A320",
}


# Helper to retrieve flight from Flights loaded, assumes flight_numbers are unique
def _get_flight_by_number(flights, flight_number):
    return next(f for f in flights if f.flight_number == flight_number)


# Helper to write a dataset exactly as given, with no default fields merged in.
# Needed for cases (like a missing required field) where the shape of the raw
# flight dict itself is the thing under test. teardown is included for free thanks to pytest
def _write_raw_dataset(tmp_path, airports, flights):
    path = tmp_path / "flights.json"
    path.write_text(json.dumps({"airports": airports, "flights": flights}))
    return path


# Helper to create a temporary dataset with one or more custom flights, each
# built from DEFAULT_FLIGHT with the given overrides applied on top.
def _write_dataset(tmp_path, flight_overrides_list):
    flights = [{**DEFAULT_FLIGHT, **overrides} for overrides in flight_overrides_list]
    return _write_raw_dataset(tmp_path, DEFAULT_AIRPORTS, flights)


# Happy path: every airport and flight in the real dataset should load
# successfully now that the JKF typo has been fixed at the source.
def test_load_dataset_loads_all_airports_and_flights_from_real_dataset(real_dataset_path):
    airports, flights = load_dataset(real_dataset_path)

    assert len(airports) == 25
    assert len(flights) == 303


# Data-integrity check: flight numbers should uniquely identify a flight.
# If the dataset ever contained a duplicate flightNumber, downstream code
# (e.g. itinerary IDs, lookups) could silently mix up two different flights.
def test_load_dataset_has_no_duplicate_flight_numbers(real_dataset_path):
    _, flights = load_dataset(real_dataset_path)

    flight_numbers = [flight.flight_number for flight in flights]
    assert len(flight_numbers) == len(set(flight_numbers))


# Dirty-data case: SP995/SP996/SP998 store `price` as a string in the real
# dataset. The loader must coerce these to floats instead of skipping them.
def test_load_dataset_coerces_string_prices_from_real_dataset(real_dataset_path):
    _, flights = load_dataset(real_dataset_path)

    assert _get_flight_by_number(flights, "SP995").price == pytest.approx(289.00)
    assert _get_flight_by_number(flights, "SP996").price == pytest.approx(99.00)
    assert _get_flight_by_number(flights, "SP998").price == pytest.approx(95.00)


# Every loaded flight should carry precomputed UTC timestamps derived from
# its origin/destination airport's timezone, not just the raw local time.
def test_load_dataset_precomputes_utc_datetimes_using_airport_timezone(real_dataset_path):
    _, flights = load_dataset(real_dataset_path)

    flight = _get_flight_by_number(flights, "SP101")
    assert flight.departure_utc == to_utc("2024-03-15T08:30:00", "America/New_York")
    assert flight.arrival_utc == to_utc("2024-03-15T11:45:00", "America/Los_Angeles")


# Test case for a flight referencing a typo'd or nonexistent airport from the list
# Should skip the flight and handle the error without throwing an exception
def test_load_dataset_skips_flight_with_unknown_airport_code(tmp_path):
    path = _write_dataset(tmp_path, [{"flightNumber": "SP995", "origin": "JKF"}])
    _, flights = load_dataset(path)

    assert flights == []


# Test case for when a price value is not a number
# Should skip the flight and handle the error without throwing an exception
def test_load_dataset_skips_flight_with_unparseable_price(tmp_path):
    path = _write_dataset(tmp_path, [{"flightNumber": "SP999", "price": "not-a-number"}])
    _, flights = load_dataset(path)

    assert flights == []


# Test case for two flights sharing the same flight number but with different
# details (e.g. a data-entry error re-using a flight number). Only the first
# occurrence in the file should be kept, the later duplicate must be dropped,
# and a warning should be logged so the drop isn't silent.
def test_load_dataset_keeps_only_first_flight_when_flight_number_is_duplicated(tmp_path, caplog):
    path = _write_dataset(tmp_path, [
        {"flightNumber": "SP101", "price": 299.0, "aircraft": "A320"},
        {"flightNumber": "SP101", "price": 999.0, "aircraft": "B737",
         "destination": "SFO"},
    ])

    with caplog.at_level(logging.WARNING):
        _, flights = load_dataset(path)

    assert len(flights) == 1
    assert flights[0].price == 299.0
    assert flights[0].aircraft == "A320"
    assert flights[0].destination == "LAX"

    assert any(
        "SP101" in record.getMessage() and "duplicate" in record.getMessage().lower()
        for record in caplog.records
    )


# Test case for a flight record missing an entire required field (not just an
# invalid value) must be skipped and logged, not crash the whole app on
# startup with a KeyError.
def test_load_dataset_skips_flight_with_missing_required_field(tmp_path):
    flight = {k: v for k, v in DEFAULT_FLIGHT.items() if k != "price"}
    path = _write_raw_dataset(tmp_path, DEFAULT_AIRPORTS, [flight])
    _, flights = load_dataset(path)

    assert flights == []


# Test case for a date field that isn't valid ISO 8601 at all (not just a
# legitimate overnight rollover) must be skipped and logged, not raise.
def test_load_dataset_skips_flight_with_unparseable_date(tmp_path):
    path = _write_dataset(tmp_path, [{"departureTime": "not-a-date"}])
    _, flights = load_dataset(path)

    assert flights == []


# Test case for a flight where the arrival time is before the departure time
# even including a timezone conversion.
# Overnight flights are fine, but this is to check for time travel.
# TODO: remove this test case when time travel exists
def test_load_dataset_skips_flight_where_arrival_is_not_after_departure(tmp_path):
    path = _write_dataset(tmp_path, [
        {"departureTime": "2024-03-15T11:45:00", "arrivalTime": "2024-03-15T08:30:00"},
    ])
    _, flights = load_dataset(path)

    assert flights == []


# Test case for an empty dataset (no airports, no flights)
def test_load_dataset_handles_empty_dataset(tmp_path):
    path = _write_raw_dataset(tmp_path, [], [])
    airports, flights = load_dataset(path)

    assert airports == {}
    assert flights == []
