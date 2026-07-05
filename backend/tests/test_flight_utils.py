from datetime import datetime, timezone

from skypath.flight_utils import is_domestic, is_domestic_connection
from skypath.models import Flight


# A connection where every airport involved is in the same country
# (e.g. JFK -> ORD -> LAX, all US) should be classified as domestic.
def test_is_domestic_true_when_all_countries_match():
    assert is_domestic("US", "US", "US") is True


# A connection is international as soon as any one airport involved is in a
# different country (e.g. JFK -> LHR -> CDG spans US/GB/FR).
def test_is_domestic_false_when_any_country_differs():
    assert is_domestic("US", "GB", "FR") is False
    assert is_domestic("US", "US", "GB") is False


# Helper to build a Flight with sensible defaults, only varying the fields a
# given test actually cares about.
def _flight(origin_country, destination_country):
    now = datetime(2024, 3, 15, tzinfo=timezone.utc)
    return Flight(
        flight_number="SP1", airline="SkyPath Airways", origin="JFK", destination="LAX",
        origin_country=origin_country, destination_country=destination_country,
        departure_local=now, arrival_local=now, departure_utc=now, arrival_utc=now,
        price=100.0, aircraft="A320",
    )


# is_domestic_connection should derive the three countries that matter (the
# inbound flight's origin/destination and the outbound flight's destination)
# straight from the two Flight objects, without the caller building the list.
def test_is_domestic_connection_true_when_all_three_countries_match():
    inbound = _flight("US", "US")
    outbound = _flight("US", "US")
    assert is_domestic_connection(inbound, outbound) is True


def test_is_domestic_connection_false_when_outbound_destination_differs():
    inbound = _flight("US", "US")
    outbound = _flight("US", "GB")
    assert is_domestic_connection(inbound, outbound) is False
