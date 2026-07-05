from datetime import date

from skypath.constants import (
    MAX_LAYOVER_MINUTES, MAX_SEGMENTS, MIN_DOMESTIC_LAYOVER_MINUTES,
    MIN_INTERNATIONAL_LAYOVER_MINUTES,
)
from skypath.flight_utils import is_domestic_connection
from skypath.models import Flight, Itinerary, Layover
from skypath.time_utils import duration_minutes


def search_itineraries(
    graph: dict[str, list[Flight]],
    origin: str,
    destination: str,
    search_date: date,
) -> list[Itinerary]:
    itineraries = []
    for flight in graph.get(origin, []):
        if flight.departure_local.date() != search_date:
            continue
        _search_from(graph, destination, path=[flight],
                     visited={origin, flight.destination}, itineraries=itineraries)

    itineraries.sort(key=lambda itinerary: itinerary.total_duration_minutes)
    return itineraries


# Main function that performs the DFS for finding the flights given a current "path", list of Flights
def _search_from(
    graph: dict[str, list[Flight]],
    destination: str,
    path: list[Flight],
    visited: set[str],
    itineraries: list[Itinerary],
) -> None:
    current = path[-1]
    if current.destination == destination:
        itineraries.append(_build_itinerary(path))
        return

    if len(path) == MAX_SEGMENTS:
        return

    for next_flight in graph.get(current.destination, []):
        if next_flight.destination in visited:
            continue

        layover_minutes = duration_minutes(current.arrival_utc, next_flight.departure_utc)
        if layover_minutes > MAX_LAYOVER_MINUTES:
            break  # outgoing flights are sorted by departure time; only later ones remain

        connection_is_domestic = is_domestic_connection(current, next_flight)
        min_layover_minutes = (
            MIN_DOMESTIC_LAYOVER_MINUTES if connection_is_domestic
            else MIN_INTERNATIONAL_LAYOVER_MINUTES
        )
        if layover_minutes < min_layover_minutes:
            continue

        path.append(next_flight)
        visited.add(next_flight.destination)
        _search_from(graph, destination, path, visited, itineraries)
        path.pop()
        visited.discard(next_flight.destination)


# Massages the Flight list into an Itinerary for consumption
def _build_itinerary(path: list[Flight]) -> Itinerary:
    layovers = []
    for current, next_flight in zip(path, path[1:]):
        connection_is_domestic = is_domestic_connection(current, next_flight)
        layovers.append(Layover(
            airport=current.destination,
            duration_minutes=duration_minutes(current.arrival_utc, next_flight.departure_utc),
            is_domestic=connection_is_domestic,
        ))

    return Itinerary(segments=list(path), layovers=layovers)
