"""Command-line interface for querying package and truck status at any time of day."""

from __future__ import annotations

import argparse
import math
from datetime import timedelta

from .data import parse_clock
from .models import Package
from .routing import DeliveryResult, simulate_day


def format_clock(time: timedelta) -> str:
    """Formats a time of day as ``"9:05 AM"``, rounding up to the next minute."""
    total_minutes = math.ceil(time.total_seconds() / 60)
    hours, minutes = divmod(total_minutes, 60)
    suffix = "AM" if hours % 24 < 12 else "PM"
    return f"{(hours - 1) % 12 + 1}:{minutes:02d} {suffix}"


def describe_status(package: Package, time: timedelta) -> str:
    status = package.status_at(time)
    if status == "Delivered":
        return f"Delivered at {format_clock(package.delivered_at)}"
    if status == "En route":
        return f"En route on {package.truck.name}"
    if status == "Delayed":
        return f"Delayed, arrives {format_clock(package.arrives_at)}"
    return status


def package_rows(packages: list[Package], time: timedelta) -> list[list[str]]:
    rows = []
    for package in packages:
        address = package.address_at(time)
        rows.append([
            str(package.id),
            address.street,
            address.city,
            address.zipcode,
            "EOD" if package.deadline is None else format_clock(package.deadline),
            f"{package.weight_kg} kg",
            package.truck.name,
            describe_status(package, time),
        ])
    return rows


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [max(len(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    lines = ["  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip() for row in [headers, *rows]]
    lines.insert(1, "  ".join("-" * width for width in widths))
    return "\n".join(lines)


PACKAGE_HEADERS = ["ID", "Address", "City", "Zip", "Deadline", "Weight", "Truck", "Status"]


def print_packages(result: DeliveryResult, time: timedelta, package_ids: list[int], label: str) -> None:
    packages = [result.packages.search(package_id) for package_id in package_ids]
    print(f"\nStatus of {label} at {format_clock(time)}:\n")
    print(render_table(PACKAGE_HEADERS, package_rows(packages, time)))


def print_summary(result: DeliveryResult) -> None:
    rows = [
        [truck.name, format_clock(truck.departs_at), format_clock(truck.returns_at),
         str(len(truck.packages)), f"{truck.miles:.1f}"]
        for truck in result.trucks
    ]
    rows.append(["Total", "", "", str(len(result.packages)), f"{result.total_miles:.1f}"])
    print(render_table(["Truck", "Departs", "Returns", "Packages", "Miles"], rows))


def all_package_ids(result: DeliveryResult) -> list[int]:
    return sorted(package.id for package in result.packages.values())


def prompt_time() -> timedelta:
    while True:
        text = input("Enter a time (for example 9:30, 10:25 AM or 1:15 PM): ")
        try:
            return parse_clock(text)
        except ValueError:
            print("That isn't a valid time.")


def prompt_package_id(result: DeliveryResult) -> int:
    while True:
        text = input("Enter a package ID: ").strip()
        try:
            if int(text) in result.packages:
                return int(text)
        except ValueError:
            pass
        print(f"No package with ID {text!r} was found.")


MENU = """
Choose an option:
  1. Status of all packages at a given time
  2. Status of one package at a given time
  3. Truck departures, returns and mileage
  4. Exit"""


def interactive(result: DeliveryResult) -> None:
    while True:
        print(MENU)
        choice = input("> ").strip()
        if choice == "1":
            print_packages(result, prompt_time(), all_package_ids(result), "all packages")
        elif choice == "2":
            package_id = prompt_package_id(result)
            print_packages(result, prompt_time(), [package_id], f"package {package_id}")
        elif choice == "3":
            print()
            print_summary(result)
        elif choice == "4":
            return
        else:
            print("Please enter 1, 2, 3 or 4.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m wgups",
        description="Route the WGUPS delivery trucks and look up package status at any time of day.",
    )
    parser.add_argument("--time", type=parse_clock, help="print package status at this time and exit")
    parser.add_argument("--package", type=int, help="with --time, show only this package")
    args = parser.parse_args(argv)
    if args.package is not None and args.time is None:
        parser.error("--package requires --time")

    result = simulate_day()
    if args.package is not None and args.package not in result.packages:
        parser.error(f"no package with ID {args.package}")

    print("WGUPS Routing Program")
    print(f"All {len(result.packages)} packages delivered in {result.total_miles:.1f} miles.\n")
    print_summary(result)

    if args.time is None:
        try:
            interactive(result)
        except (EOFError, KeyboardInterrupt):
            print()
        return

    if args.package is None:
        print_packages(result, args.time, all_package_ids(result), "all packages")
    else:
        print_packages(result, args.time, [args.package], f"package {args.package}")
