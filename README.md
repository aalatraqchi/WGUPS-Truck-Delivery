# WGUPS Routing Program

[![CI](https://github.com/aalatraqchi/WGUPS-Truck-Delivery/actions/workflows/ci.yml/badge.svg)](https://github.com/aalatraqchi/WGUPS-Truck-Delivery/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A package delivery routing program written in Python that plans routes for three trucks, delivers 40 packages on time under real-world constraints, and lets users check the status of any package or truck at any time of day.

It routes every package in **122.1 miles**, under the 140-mile limit, using a greedy nearest-neighbor algorithm and a hash table built from scratch.

```text
$ python -m wgups --time 10:30
WGUPS Routing Program
All 40 packages delivered in 122.1 miles.

Truck    Departs   Returns   Packages  Miles
-------  --------  --------  --------  -----
Truck 1  8:00 AM   10:05 AM  16        37.5
Truck 2  9:05 AM   11:08 AM  11        36.8
Truck 3  10:05 AM  12:45 PM  13        47.8
Total                        40        122.1

Status of all packages at 10:30 AM:

ID  Address            City              Zip    Deadline  Weight  Truck    Status
--  -----------------  ----------------  -----  --------  ------  -------  --------------------
1   195 W Oakland Ave  Salt Lake City    84115  10:30 AM  21 kg   Truck 1  Delivered at 8:39 AM
2   2530 S 500 E       Salt Lake City    84106  EOD       44 kg   Truck 3  En route on Truck 3
3   233 Canyon Rd      Salt Lake City    84103  EOD       2 kg    Truck 2  En route on Truck 2
6   3060 Lester St     West Valley City  84119  10:30 AM  88 kg   Truck 2  Delivered at 9:45 AM
9   410 S State St     Salt Lake City    84111  EOD       2 kg    Truck 3  En route on Truck 3
...
```

## Features

- **Route Planning:** Nearest-neighbor routing for each truck, starting and ending at the hub.
- **Constraint Handling:** Deadlines, truck-specific packages, delayed packages, packages that must travel together, a two-driver limit, and an address that is only corrected mid-day.
- **Package Lookup:** A chaining hash table with automatic resizing stores every package for O(1) average lookups by ID.
- **Status at Any Time:** See whether each package is delayed, at the hub, en route, or delivered (and when) at any time of day.
- **Interactive Menu:** Look up all packages, a single package, or truck mileage from the terminal.
- **Scriptable CLI:** Print a status snapshot with `--time` and `--package` for quick checks.
- **Automated Testing:** 31 tests verify the hash table, the CLI, and every delivery requirement.

## Tech Stack

- **Language:** Python 3.10+ (standard library only, no dependencies)
- **Data Structures:** Custom chaining hash table, symmetric distance matrix
- **Algorithm:** Greedy nearest-neighbor routing
- **Testing:** unittest
- **CI:** GitHub Actions

## Getting Started

Clone the repository and run the interactive program from its root:

```bash
git clone https://github.com/aalatraqchi/WGUPS-Truck-Delivery.git
cd WGUPS-Truck-Delivery
python -m wgups
```

Use `python3` instead of `python` if that's how Python 3 is installed on your system.

Print a status snapshot and exit:

```bash
python -m wgups --time 10:30                # every package at 10:30 AM
python -m wgups --time "1:15 PM" --package 9  # one package
```

## Testing

```bash
python -m unittest
```

The routing tests check the full day against the project requirements: all 40 packages delivered, every deadline met, under 140 total miles, at most 16 packages per truck, no more than two trucks on the road, and every special note honored.

## Current Scope

The program is built for the Salt Lake City scenario in the [project brief](docs/PROJECT-BRIEF.md). Package, address, and distance data are read from the CSV files in [`data/`](data/), so the routing works for any number of packages and locations. Which packages go on which truck and when each truck departs are set by hand in [`wgups/data.py`](wgups/data.py), based on the packages' special notes.

Nearest-neighbor routing stays well under the mileage limit but doesn't guarantee the shortest possible route.

This project was originally developed for the Data Structures and Algorithms II course at Western Governors University.

## Documentation

- [Algorithm & Design](docs/ALGORITHM.md): routing approach, data structures, complexity, and constraint handling
- [Project Brief](docs/PROJECT-BRIEF.md): the original scenario, requirements, and assumptions

## License

[MIT](LICENSE). The scenario and the package, address, and distance data in `data/` come from the WGU course materials and are not covered by this license.
