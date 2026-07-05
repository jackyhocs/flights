from datetime import date, datetime, timezone

from skypath.data_loader import load_dataset
from skypath.graph import build_graph
from skypath.models import Flight
from skypath.search import search_itineraries

SEARCH_DATE = date(2024, 3, 15)


# Helper to build a Flight with sensible defaults, only varying the fields a
# given test actually cares about.
def _flight(flight_number, origin, destination, departure_utc, arrival_utc,
            origin_country="US", destination_country="US"):
    return Flight(
        flight_number=flight_number,
        airline="SkyPath Airways",
        origin=origin,
        destination=destination,
        origin_country=origin_country,
        destination_country=destination_country,
        departure_local=departure_utc,
        arrival_local=arrival_utc,
        departure_utc=departure_utc,
        arrival_utc=arrival_utc,
        price=100.0,
        aircraft="A320",
    )


# Fixture loading the real dataset once per test, pre-built into a graph, so
# each required-scenario test just runs a search against it.
def _real_graph(real_dataset_path):
    _, flights = load_dataset(real_dataset_path)
    return build_graph(flights)


# Required scenario 1: JFK -> LAX should return both a direct flight and
# multi-stop options, sorted shortest total duration first.
def test_jfk_to_lax_returns_direct_and_multi_stop_itineraries_sorted_by_duration(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "JFK", "LAX", SEARCH_DATE)

    assert len(itineraries) > 0
    assert any(itinerary.stops == 0 for itinerary in itineraries)
    assert any(itinerary.stops > 0 for itinerary in itineraries)
    durations = [itinerary.total_duration_minutes for itinerary in itineraries]
    assert durations == sorted(durations)


# Required scenario 2: SFO -> NRT is an international route, so every
# connection found must respect the 90-minute international minimum layover.
def test_sfo_to_nrt_connections_respect_international_minimum_layover(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "SFO", "NRT", SEARCH_DATE)

    assert len(itineraries) > 0
    for itinerary in itineraries:
        for layover in itinerary.layovers:
            if not layover.is_domestic:
                assert layover.duration_minutes >= 90


# Required scenario 3: BOS -> SEA has no direct flight in the dataset, so
# every itinerary returned must involve at least one stop.
def test_bos_to_sea_has_no_direct_flight_and_only_returns_connections(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "BOS", "SEA", SEARCH_DATE)

    assert len(itineraries) > 0
    assert all(itinerary.stops >= 1 for itinerary in itineraries)


# Required scenario 4: searching an airport against itself should not error,
# it should simply yield no valid itineraries.
def test_jfk_to_jfk_returns_no_itineraries(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "JFK", "JFK", SEARCH_DATE)

    assert itineraries == []


# Required scenario 5: an origin code with no outgoing flights in the graph
# (e.g. an invalid airport) should yield no itineraries rather than raising.
def test_unknown_origin_code_returns_no_itineraries(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "XXX", "LAX", SEARCH_DATE)

    assert itineraries == []


# Required scenario 6: SYD -> LAX crosses the international date line, so the
# local arrival time appears "before" the local departure time. Duration must
# still be computed correctly by comparing UTC timestamps.
def test_syd_to_lax_computes_correct_duration_across_date_line(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "SYD", "LAX", SEARCH_DATE)

    assert len(itineraries) > 0
    for itinerary in itineraries:
        assert itinerary.total_duration_minutes > 0


# Layover boundary: a domestic connection with exactly 45 minutes is valid,
# but 44 minutes falls just short of the minimum and must be rejected.
def test_domestic_layover_boundary_44_minutes_rejected_45_minutes_accepted():
    inbound = _flight(
        "SP1", "JFK", "ORD",
        datetime(2024, 3, 15, 8, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 10, tzinfo=timezone.utc),
    )
    too_short = _flight(
        "SP2", "ORD", "LAX",
        datetime(2024, 3, 15, 10, 44, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 13, tzinfo=timezone.utc),
    )
    long_enough = _flight(
        "SP3", "ORD", "LAX",
        datetime(2024, 3, 15, 10, 45, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 13, tzinfo=timezone.utc),
    )

    graph = build_graph([inbound, too_short, long_enough])

    itineraries = search_itineraries(graph, "JFK", "LAX", SEARCH_DATE)

    assert len(itineraries) == 1
    assert itineraries[0].segments[-1].flight_number == "SP3"


# Layover boundary: an international connection with exactly 90 minutes is
# valid, but 89 minutes falls just short of the minimum and must be rejected.
def test_international_layover_boundary_89_minutes_rejected_90_minutes_accepted():
    inbound = _flight(
        "SP1", "JFK", "LHR",
        datetime(2024, 3, 15, 8, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 16, tzinfo=timezone.utc),
        origin_country="US", destination_country="GB",
    )
    too_short = _flight(
        "SP2", "LHR", "CDG",
        datetime(2024, 3, 15, 17, 29, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 19, tzinfo=timezone.utc),
        origin_country="GB", destination_country="FR",
    )
    long_enough = _flight(
        "SP3", "LHR", "CDG",
        datetime(2024, 3, 15, 17, 30, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 19, tzinfo=timezone.utc),
        origin_country="GB", destination_country="FR",
    )

    graph = build_graph([inbound, too_short, long_enough])

    itineraries = search_itineraries(graph, "JFK", "CDG", SEARCH_DATE)

    assert len(itineraries) == 1
    assert itineraries[0].segments[-1].flight_number == "SP3"


# Layover boundary: a 6-hour (360-minute) layover is the maximum allowed, but
# 361 minutes exceeds it and the connection must be rejected.
def test_layover_boundary_360_minutes_accepted_361_minutes_rejected():
    inbound = _flight(
        "SP1", "JFK", "ORD",
        datetime(2024, 3, 15, 8, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 10, tzinfo=timezone.utc),
    )
    within_max = _flight(
        "SP2", "ORD", "LAX",
        datetime(2024, 3, 15, 16, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 18, tzinfo=timezone.utc),
    )
    over_max = _flight(
        "SP3", "ORD", "LAX",
        datetime(2024, 3, 15, 16, 1, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 18, tzinfo=timezone.utc),
    )

    graph = build_graph([inbound, within_max, over_max])

    itineraries = search_itineraries(graph, "JFK", "LAX", SEARCH_DATE)

    assert len(itineraries) == 1
    assert itineraries[0].segments[-1].flight_number == "SP2"


# A search should never return an itinerary with more than 2 stops (3 segments).
def test_search_never_returns_itineraries_exceeding_max_stops(real_dataset_path):
    graph = _real_graph(real_dataset_path)

    itineraries = search_itineraries(graph, "JFK", "LAX", SEARCH_DATE)

    assert all(itinerary.stops <= 2 for itinerary in itineraries)


# The search must never revisit an airport already used earlier in the same
# itinerary, since that would represent a pointless loop rather than progress
# toward the destination.
def test_search_never_revisits_an_airport_within_the_same_itinerary():
    out_and_back = _flight(
        "SP1", "JFK", "ORD",
        datetime(2024, 3, 15, 8, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 10, tzinfo=timezone.utc),
    )
    back_to_start = _flight(
        "SP2", "ORD", "JFK",
        datetime(2024, 3, 15, 11, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 13, tzinfo=timezone.utc),
    )
    onward = _flight(
        "SP3", "JFK", "LAX",
        datetime(2024, 3, 15, 14, tzinfo=timezone.utc),
        datetime(2024, 3, 15, 17, tzinfo=timezone.utc),
    )

    graph = build_graph([out_and_back, back_to_start, onward])

    itineraries = search_itineraries(graph, "JFK", "LAX", SEARCH_DATE)

    assert len(itineraries) == 1
    assert [segment.flight_number for segment in itineraries[0].segments] == ["SP3"]
