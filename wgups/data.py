"""Loads the package, location and distance data and the day's truck plan."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from .hash_table import HashTable
from .models import Address, Package, Truck

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

HUB_LOCATION_ID = 0
"""The WGUPS hub (Western Governors University, 4001 South 700 East)."""

TRUCK_CAPACITY = 16
DRIVER_COUNT = 2
START_OF_DAY = timedelta(hours=8)

# Package IDs loaded onto each truck. The split was chosen by hand from the
# packages' special notes: truck-2-only packages, packages delayed until 9:05,
# packages that must be delivered together, and early deadlines.
TRUCK_LOADS: dict[str, list[int]] = {
    "Truck 1": [1, 4, 7, 13, 14, 15, 16, 19, 20, 21, 29, 30, 34, 37, 39, 40],
    "Truck 2": [3, 5, 6, 18, 25, 26, 28, 31, 32, 36, 38],
    "Truck 3": [2, 8, 9, 10, 11, 12, 17, 22, 23, 24, 27, 33, 35],
}

# Departure times. Truck 1 leaves at the start of the day; truck 2 waits for the
# delayed flight packages. With only two drivers, truck 3 leaves when the first
# driver returns to the hub, so its departure is set during routing.
DEPARTURE_TIMES: dict[str, timedelta | None] = {
    "Truck 1": START_OF_DAY,
    "Truck 2": timedelta(hours=9, minutes=5),
    "Truck 3": None,
}

# Package 9 is listed with the wrong address; the correct one is only known at 10:20.
ADDRESS_CORRECTIONS: dict[int, tuple[timedelta, str, str]] = {
    9: (timedelta(hours=10, minutes=20), "410 S State St", "84111"),
}


@dataclass
class DeliveryData:
    packages: HashTable
    """Package ID -> Package."""
    trucks: list[Truck]
    distances: DistanceTable


class DistanceTable:
    """Symmetric distance matrix read from a lower-triangular CSV."""

    def __init__(self, rows: list[list[float]]) -> None:
        self._rows = rows

    def between(self, a: int, b: int) -> float:
        """Miles between two location IDs, in either direction. O(1)."""
        if a < b:
            a, b = b, a
        return self._rows[a][b]

    def __len__(self) -> int:
        return len(self._rows)


_CLOCK = re.compile(r"([0-9]{1,2}):([0-9]{2})\s*([AP]M)?", re.IGNORECASE)
_DELAYED_NOTE = re.compile(r"will not arrive to depot until ([0-9]{1,2}:[0-9]{2} [AP]M)", re.IGNORECASE)


def parse_clock(text: str) -> timedelta:
    """Parses a time of day such as ``"9:05"``, ``"14:45"``, ``"10:30 AM"`` or ``"2:15 PM"``."""
    match = _CLOCK.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"invalid time: {text!r}")
    hours, minutes, suffix = int(match[1]), int(match[2]), (match[3] or "").upper()
    if minutes > 59 or (suffix and not 1 <= hours <= 12) or hours > 23:
        raise ValueError(f"invalid time: {text!r}")
    if suffix:
        hours = hours % 12 + (12 if suffix == "PM" else 0)
    return timedelta(hours=hours, minutes=minutes)


def _read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return [row for row in csv.reader(file) if row]


def load_distances(path: Path) -> DistanceTable:
    rows = []
    for index, row in enumerate(_read_csv(path)):
        while row and not row[-1].strip():
            row.pop()
        if len(row) != index + 1:
            raise ValueError(f"{path.name} row {index + 1} has {len(row)} values; expected {index + 1}")
        rows.append([float(cell) for cell in row])
    return DistanceTable(rows)


def load_location_ids(path: Path) -> dict[str, int]:
    """Maps each street address to its 0-based index in the distance table."""
    return {street: int(location_id) - 1 for location_id, _name, street in _read_csv(path)}


def load_packages(path: Path, location_ids: dict[str, int]) -> list[Package]:
    packages = []
    for row in _read_csv(path):
        package_id, street, city, state, zipcode, deadline, weight = row[:7]
        package = Package(
            id=int(package_id),
            address=Address(street, city, state, zipcode, location_ids[street]),
            deadline=None if deadline == "EOD" else parse_clock(deadline),
            weight_kg=int(weight),
            note=row[7] if len(row) > 7 else "",
        )
        delayed = _DELAYED_NOTE.search(package.note)
        if delayed:
            package.arrives_at = parse_clock(delayed[1])
        if package.id in ADDRESS_CORRECTIONS:
            known_at, new_street, new_zip = ADDRESS_CORRECTIONS[package.id]
            package.correction_time = known_at
            package.corrected_address = Address(new_street, city, state, new_zip, location_ids[new_street])
        packages.append(package)
    return packages


def load_delivery_data(data_dir: Path = DATA_DIR) -> DeliveryData:
    """Reads the CSV files and loads every package onto its planned truck."""
    location_ids = load_location_ids(data_dir / "locations.csv")
    distances = load_distances(data_dir / "distances.csv")
    packages = load_packages(data_dir / "packages.csv", location_ids)

    table = HashTable()
    for package in packages:
        table.insert(package.id, package)

    trucks = []
    for name, package_ids in TRUCK_LOADS.items():
        if len(package_ids) > TRUCK_CAPACITY:
            raise ValueError(f"{name} is loaded with {len(package_ids)} packages; the limit is {TRUCK_CAPACITY}")
        truck = Truck(name, departs_at=DEPARTURE_TIMES[name])
        for package_id in package_ids:
            package = table.search(package_id)
            if package is None:
                raise ValueError(f"{name} is loaded with unknown package {package_id}")
            package.truck = truck
            truck.packages.append(package)
        trucks.append(truck)

    unassigned = [p.id for p in packages if p.truck is None]
    if unassigned:
        raise ValueError(f"packages not loaded on any truck: {unassigned}")

    return DeliveryData(table, trucks, distances)
