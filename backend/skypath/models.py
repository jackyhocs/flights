from dataclasses import dataclass, field
from datetime import datetime

from skypath.time_utils import duration_minutes


@dataclass(frozen=True)
class Airport:
    code: str
    name: str
    city: str
    country: str
    timezone: str


@dataclass(frozen=True)
class Flight:
    flight_number: str
    airline: str
    origin: str
    destination: str
    origin_country: str
    destination_country: str
    departure_local: datetime
    arrival_local: datetime
    departure_utc: datetime
    arrival_utc: datetime
    price: float
    aircraft: str


@dataclass(frozen=True)
class Layover:
    airport: str
    duration_minutes: int
    is_domestic: bool


@dataclass(frozen=True)
class Itinerary:
    segments: list[Flight]
    layovers: list[Layover] = field(default_factory=list)

    @property
    def stops(self) -> int:
        return len(self.segments) - 1

    @property
    def total_duration_minutes(self) -> int:
        return duration_minutes(self.segments[0].departure_utc, self.segments[-1].arrival_utc)

    @property
    def total_price(self) -> float:
        return sum(segment.price for segment in self.segments)

    # An itinerary is domestic only if every leg stays within one country.
    # With layovers, each one's own domestic/international type already
    # captures this transitively (it was derived from its adjacent legs), so
    # checking all of them is sufficient. A nonstop itinerary has no layovers,
    # so origin/destination country is compared directly instead.
    @property
    def is_domestic(self) -> bool:
        if not self.layovers:
            return self.segments[0].origin_country == self.segments[-1].destination_country
        return all(layover.is_domestic for layover in self.layovers)
