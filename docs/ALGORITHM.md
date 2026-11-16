# Algorithm & Design

## Code layout

```text
wgups/
├── hash_table.py   Chaining hash table that stores packages by ID
├── models.py       Address, Package and Truck data classes, and status at a given time
├── data.py         CSV loading, the distance table, and the day's truck plan
├── routing.py      Nearest-neighbor routing and driver scheduling
└── cli.py          Interactive menu and command-line snapshot
tests/              unittest suites for the hash table, routing requirements and CLI
data/               Package, location and distance CSV files
```

`routing.simulate_day()` loads the data, routes every truck, and returns the results. The CLI and the tests both use it, so the tests check exactly what users see.

## Routing

Each truck runs a greedy **nearest-neighbor** route:

1. Start at the hub at the truck's departure time.
2. From the current location, pick the closest address among the truck's undelivered packages.
3. Drive there, advancing the clock by `miles / 18 mph`, and deliver every package for that address.
4. Repeat until the truck is empty, then return to the hub.

Nearest neighbor was chosen because it's simple, fast, and adapts to any number of packages and locations without changes. It isn't guaranteed to find the shortest route, but here it delivers everything in 122.1 miles against a 140-mile limit.

| Truck | Departs | Returns | Packages | Miles |
| --- | --- | --- | --- | --- |
| Truck 1 | 8:00 AM | 10:05 AM | 16 | 37.5 |
| Truck 2 | 9:05 AM | 11:08 AM | 11 | 36.8 |
| Truck 3 | 10:05 AM | 12:45 PM | 13 | 47.8 |
| **Total** | | | **40** | **122.1** |

## Constraint handling

| Constraint | How it's met |
| --- | --- |
| 16 packages per truck | Truck loads are checked against the capacity when the data loads. |
| Leave no earlier than 8:00 AM | Every driver starts the day free at 8:00 AM. |
| Two drivers for three trucks | Trucks are given to drivers in departure order. Truck 3 has no fixed departure, so it leaves when the first truck returns and frees its driver. Routing fails with an error if a fixed departure has no free driver. |
| Packages delayed until 9:05 AM | They're loaded on truck 2, which departs at 9:05 AM. Arrival times are read from the package notes, routing fails if a truck would leave before its packages arrive, and status lookups show these packages as delayed until then. |
| "Can only be on truck 2" | Those packages are loaded on truck 2. |
| "Must be delivered with" groups | Packages 13, 14, 15, 16, 19 and 20 are all loaded on truck 1. |
| Early deadlines | Packages due by 9:00 or 10:30 AM go on the trucks that leave first. |
| Package 9's address is corrected at 10:20 AM | The router skips a package until its correct address is known, and the truck waits if nothing else is left. Status lookups before 10:20 show the original, wrong address. |

The truck loads are assigned by hand in `wgups/data.py` from the special notes. The routing itself is fully automatic.

## Data structures

**Hash table.** Packages are stored in a chaining hash table keyed by package ID. Each bucket holds a list of key/value pairs, so collisions are kept in the same bucket. When the number of items exceeds the number of buckets, the table doubles in size and rehashes, which keeps chains short as the package count grows.

**Distance table.** The CSV only stores the lower triangle of the distance matrix because distances are the same in both directions. `DistanceTable.between(a, b)` swaps its arguments when needed, so lookups work in either direction.

**Location index.** Each street address maps to its row in the distance table through a dictionary built at load time, so finding a package's location is a single lookup.

## Complexity

With *n* packages and *L* locations:

| Operation | Time | Notes |
| --- | --- | --- |
| Hash table insert, search, remove | O(1) average, O(n) worst case | Resizing is O(n) but happens rarely, so inserts are O(1) amortized. |
| Distance lookup | O(1) | Direct index into the matrix |
| Loading the data | O(n + L²) | Reading the distance matrix dominates |
| Routing one truck with *k* packages | O(k²) | Up to *k* stops, each scanning the remaining packages |
| Routing the whole day | O(n²) worst case | |
| Status of every package at a time | O(n) | One hash lookup per package |
| Space | O(n + L²) | Packages plus the distance matrix |

## Possible improvements

- **Automatic truck loading.** Assign packages to trucks from their notes and deadlines instead of by hand.
- **Route improvement.** Apply 2-opt swaps after nearest neighbor to shorten each route further.
- **Deadline-aware routing.** Weigh deadlines into the choice of next stop instead of relying on the truck plan to keep early packages on early trucks.
