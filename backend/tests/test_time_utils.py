from datetime import datetime, timezone

from skypath.models import Airport
from skypath.time_utils import duration_minutes, to_utc

JFK = Airport("JFK", "John F. Kennedy International", "New York", "US", "America/New_York")
LAX = Airport("LAX", "Los Angeles International", "Los Angeles", "US", "America/Los_Angeles")
SYD = Airport("SYD", "Sydney Kingsford Smith", "Sydney", "AU", "Australia/Sydney")


# A local ISO timestamp should convert to the correct UTC instant for its
# airport's timezone, not be treated as if it were already UTC.
# 2024-03-15 is after US DST starts (Mar 10), so New York is UTC-4 (EDT).
def test_to_utc_converts_local_time_using_airport_timezone():
    result = to_utc("2024-03-15T08:30:00", "America/New_York")
    assert result == datetime(2024, 3, 15, 12, 30, tzinfo=timezone.utc)


# Timezone conversion must also be correct for a southern-hemisphere airport,
# whose daylight-saving calendar is the opposite of the US's.
# 2024-03-15 is before Sydney's DST ends (first Sunday in April), so AEDT = UTC+11.
def test_to_utc_handles_southern_hemisphere_daylight_saving():
    result = to_utc("2024-03-15T23:00:00", "Australia/Sydney")
    assert result == datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc)


# The simple case: departure and arrival airports share a timezone, so the
# duration is just the plain difference between the two local times.
def test_duration_minutes_handles_same_timezone_flight():
    departure = to_utc("2024-03-15T08:30:00", "America/New_York")
    arrival = to_utc("2024-03-15T11:45:00", "America/New_York")
    assert duration_minutes(departure, arrival) == 195


# This is the required SYD -> LAX test case from the spec. SYD departs late
# on 2024-03-15 local time and, due to the international date line, LAX
# arrival lands earlier in local calendar time on the same date. Naively
# comparing local time strings would suggest a negative or nonsensical
# duration; UTC-based math must still produce a correct, positive duration.
def test_duration_minutes_handles_date_line_crossing_syd_to_lax():
    departure_utc = to_utc("2024-03-15T23:00:00", "Australia/Sydney")
    arrival_utc = to_utc("2024-03-15T19:00:00", "America/Los_Angeles")
    duration = duration_minutes(departure_utc, arrival_utc)
    assert duration > 0
    assert duration == 840
