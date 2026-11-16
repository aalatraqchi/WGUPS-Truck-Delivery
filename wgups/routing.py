"""Greedy nearest-neighbor routing for the delivery trucks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from .data import DATA_DIR, DRIVER_COUNT, HUB_LOCATION_ID, START_OF_DAY, DeliveryData, DistanceTable, load_delivery_data
from .hash_table import HashTable
from .models import Truck

TRUCK_SPEED_MPH = 18.0


@dataclass
class DeliveryResult:
    packages: HashTable
    trucks: list[Truck]

    @property
    def total_miles(self) -> float:
        return sum(truck.miles for truck in self.trucks)


def deliver(truck: Truck, distances: DistanceTable) -> None:
    """Drives ``truck`` from the hub to every package's address and back.

    At each stop the truck goes to the closest address among its undelivered
    packages whose correct address is currently known, and delivers every
    package for that address. A package with a pending address correction is
    skipped until the correction is known; if nothing else is left, the truck
    waits for it. Runs in O(n^2) for n packages on the truck.
    """
    time = truck.departs_at
    here = HUB_LOCATION_ID
    truck.route = [here]
    pending = list(truck.packages)

    while pending:
        candidates = [p for p in pending if p.address_known(time)]
        if not candidates:
            time = min(p.correction_time for p in pending)
            continue

        nearest = min(candidates, key=lambda p: distances.between(here, p.address_at(time).location_id))
        destination = nearest.address_at(time).location_id
        time = _drive(truck, distances, here, destination, time)
        here = destination
        truck.route.append(here)

        for package in candidates:
            if package.address_at(time).location_id == here:
                package.delivered_at = time
        pending = [p for p in pending if p.delivered_at is None]

    truck.returns_at = _drive(truck, distances, here, HUB_LOCATION_ID, time)
    truck.route.append(HUB_LOCATION_ID)


def _drive(truck: Truck, distances: DistanceTable, origin: int, destination: int, time: timedelta) -> timedelta:
    miles = distances.between(origin, destination)
    truck.miles += miles
    return time + timedelta(hours=miles / TRUCK_SPEED_MPH)


def run_deliveries(data: DeliveryData, drivers: int = DRIVER_COUNT) -> DeliveryResult:
    """Routes every truck, never putting more trucks on the road than there are drivers.

    Trucks with a fixed departure time go first. A truck without one leaves as
    soon as a driver is free: when the first truck back at the hub returns.
    """
    driver_free_at = [START_OF_DAY] * drivers
    scheduled = sorted((t for t in data.trucks if t.departs_at is not None), key=lambda t: t.departs_at)
    waiting = [t for t in data.trucks if t.departs_at is None]

    for truck in scheduled + waiting:
        driver = min(range(drivers), key=lambda d: driver_free_at[d])
        if truck.departs_at is None:
            truck.departs_at = driver_free_at[driver]
        elif truck.departs_at < driver_free_at[driver]:
            raise ValueError(f"no driver is free for {truck.name} at its {truck.departs_at} departure")
        _check_packages_have_arrived(truck)
        deliver(truck, data.distances)
        driver_free_at[driver] = truck.returns_at

    return DeliveryResult(data.packages, data.trucks)


def _check_packages_have_arrived(truck: Truck) -> None:
    for package in truck.packages:
        if package.arrives_at is not None and package.arrives_at > truck.departs_at:
            raise ValueError(f"{truck.name} departs before package {package.id} arrives at the hub")


def simulate_day(data_dir: Path = DATA_DIR) -> DeliveryResult:
    """Loads the day's data and runs every delivery route."""
    return run_deliveries(load_delivery_data(data_dir))
