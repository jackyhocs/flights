from datetime import datetime, timezone

from skypath.models import Airport
from skypath.time_utils import duration_minutes, is_domestic, to_utc

JFK = Airport("JFK", "John F. Kennedy International", "New York", "US", "America/New_York")
ORD = Airport("ORD", "O'Hare International", "Chicago", "US", "America/Chicago")
LAX = Airport("LAX", "Los Angeles International", "Los Angeles", "US", "America/Los_Angeles")
LHR = Airport("LHR", "Heathrow", "London", "GB", "Europe/London")
CDG = Airport("CDG", "Charles de Gaulle", "Paris", "FR", "Europe/Paris")
SYD = Airport("SYD", "Sydney Kingsford Smith", "Sydney", "AU", "Australia/Sydney")


def test_to_utc_converts_local_time_using_airport_timezone():
    # Purpose: a local ISO timestamp should convert to the correct UTC instant
    # for its airport's timezone, not be treated as if it were already UTC.
    # 2024-03-15 is after US DST starts (Mar 10), so New York is UTC-4 (EDT).
    result = to_utc("2024-03-15T08:30:00", "America/New_York")
    assert result == datetime(2024, 3, 15, 12, 30, tzinfo=timezone.utc)


def test_to_utc_handles_southern_hemisphere_daylight_saving():
    # Purpose: timezone conversion must also be correct for a southern-hemisphere
    # airport, whose daylight-saving calendar is the opposite of the US's.
    # 2024-03-15 is before Sydney's DST ends (first Sunday in April), so AEDT = UTC+11.
    result = to_utc("2024-03-15T23:00:00", "Australia/Sydney")
    assert result == datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc)


def test_duration_minutes_handles_same_timezone_flight():
    # Purpose: the simple case - departure and arrival airports share a timezone,
    # so the duration is just the plain difference between the two local times.
    departure = to_utc("2024-03-15T08:30:00", "America/New_York")
    arrival = to_utc("2024-03-15T11:45:00", "America/New_York")
    assert duration_minutes(departure, arrival) == 195


def test_duration_minutes_handles_date_line_crossing_syd_to_lax():
    # Purpose: this is the required SYD -> LAX test case from the spec.
    # SYD departs late on 2024-03-15 local time and, due to the international date
    # line, LAX arrival lands earlier in local calendar time on the same date.
    # Naively comparing local time strings would suggest a negative or nonsensical
    # duration; UTC-based math must still produce a correct, positive duration.
    departure_utc = to_utc("2024-03-15T23:00:00", "Australia/Sydney")
    arrival_utc = to_utc("2024-03-15T19:00:00", "America/Los_Angeles")
    duration = duration_minutes(departure_utc, arrival_utc)
    assert duration > 0
    assert duration == 840


def test_is_domestic_true_when_all_airports_share_a_country():
    # Purpose: a connection where every airport involved is in the same country
    # (e.g. JFK -> ORD -> LAX, all US) should be classified as domestic.
    assert is_domestic([JFK, ORD, LAX]) is True


def test_is_domestic_false_when_any_airport_is_in_a_different_country():
    # Purpose: a connection is international as soon as any one airport involved
    # is in a different country (e.g. JFK -> LHR -> CDG spans US/GB/FR).
    assert is_domestic([JFK, LHR, CDG]) is False
    assert is_domestic([JFK, ORD, LHR]) is False
