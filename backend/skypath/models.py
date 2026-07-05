from dataclasses import dataclass, field
from datetime import datetime


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
        delta = self.segments[-1].arrival_utc - self.segments[0].departure_utc
        return int(delta.total_seconds() // 60)

    @property
    def total_price(self) -> float:
        return sum(segment.price for segment in self.segments)
