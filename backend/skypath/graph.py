from collections import defaultdict

from skypath.models import Flight


def build_graph(flights: list[Flight]) -> dict[str, list[Flight]]:
    graph = defaultdict(list)
    for flight in flights:
        graph[flight.origin].append(flight)

    for outgoing_flights in graph.values():
        outgoing_flights.sort(key=lambda flight: flight.departure_utc)

    return dict(graph)
