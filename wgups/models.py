"""Domain objects: delivery addresses, packages and trucks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zipcode: str
    location_id: int
    """Row/column index of this address in the distance table."""


@dataclass
class Package:
    id: int
    address: Address
    deadline: timedelta | None
    """Delivery deadline as a time of day, or ``None`` for end of day."""
    weight_kg: int
    note: str = ""
    corrected_address: Address | None = None
    correction_time: timedelta | None = None
    """When ``corrected_address`` becomes known. Before then, ``address`` is wrong."""
    arrives_at: timedelta | None = None
    """When a delayed package reaches the hub, or ``None`` if it's there at the start of the day."""
    truck: Truck | None = None
    delivered_at: timedelta | None = None

    def address_at(self, time: timedelta) -> Address:
        """Returns the address the dispatcher knows about at ``time``."""
        if self.corrected_address is not None and time >= self.correction_time:
            return self.corrected_address
        return self.address

    def address_known(self, time: timedelta) -> bool:
        """Whether the package's correct delivery address is known at ``time``."""
        return self.corrected_address is None or time >= self.correction_time

    def status_at(self, time: timedelta) -> str:
        if self.delivered_at is not None and time >= self.delivered_at:
            return "Delivered"
        if self.truck is not None and self.truck.departs_at is not None and time >= self.truck.departs_at:
            return "En route"
        if self.arrives_at is not None and time < self.arrives_at:
            return "Delayed"
        return "At the hub"


@dataclass
class Truck:
    name: str
    packages: list[Package] = field(default_factory=list)
    departs_at: timedelta | None = None
    returns_at: timedelta | None = None
    miles: float = 0.0
    route: list[int] = field(default_factory=list)
    """Location IDs visited in order, starting and ending at the hub."""
