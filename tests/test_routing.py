"""Checks the routed day against every requirement in the project brief."""

import unittest
from datetime import timedelta

from wgups.data import TRUCK_CAPACITY, load_delivery_data, parse_clock
from wgups.routing import run_deliveries, simulate_day


def at(clock):
    return parse_clock(clock)


class DeliveryRequirementsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = simulate_day()
        cls.packages = {p.id: p for p in cls.result.packages.values()}
        cls.trucks = {t.name: t for t in cls.result.trucks}

    def test_every_package_is_delivered(self):
        self.assertEqual(len(self.packages), 40)
        undelivered = [p.id for p in self.packages.values() if p.delivered_at is None]
        self.assertEqual(undelivered, [])

    def test_total_distance_is_under_140_miles(self):
        self.assertLess(self.result.total_miles, 140)

    def test_every_deadline_is_met(self):
        late = [p.id for p in self.packages.values() if p.deadline and p.delivered_at > p.deadline]
        self.assertEqual(late, [])

    def test_trucks_respect_capacity(self):
        for truck in self.result.trucks:
            self.assertLessEqual(len(truck.packages), TRUCK_CAPACITY, truck.name)

    def test_no_truck_leaves_before_8am(self):
        for truck in self.result.trucks:
            self.assertGreaterEqual(truck.departs_at, at("8:00"), truck.name)

    def test_only_two_drivers_are_on_the_road(self):
        events = sorted(
            [(t.departs_at, 1) for t in self.result.trucks] + [(t.returns_at, -1) for t in self.result.trucks]
        )
        on_road = 0
        for _, change in events:
            on_road += change
            self.assertLessEqual(on_road, 2)

    def test_truck_2_only_packages(self):
        for package_id in (3, 18, 36, 38):
            self.assertEqual(self.packages[package_id].truck.name, "Truck 2", package_id)

    def test_delayed_packages_leave_after_their_flight_lands(self):
        for package_id in (6, 25, 28, 32):
            self.assertGreaterEqual(self.packages[package_id].truck.departs_at, at("9:05"), package_id)

    def test_grouped_packages_travel_together(self):
        trucks = {self.packages[i].truck.name for i in (13, 14, 15, 16, 19, 20)}
        self.assertEqual(len(trucks), 1)

    def test_package_9_is_routed_only_after_its_address_is_corrected(self):
        package = self.packages[9]
        self.assertGreaterEqual(package.delivered_at, at("10:20"))
        self.assertEqual(package.address_at(package.delivered_at).street, "410 S State St")
        self.assertEqual(package.address_at(at("10:19")).street, "300 State St")
        self.assertEqual(package.address_at(at("10:20")).zipcode, "84111")

    def test_routes_start_and_end_at_the_hub(self):
        for truck in self.result.trucks:
            self.assertEqual(truck.route[0], 0, truck.name)
            self.assertEqual(truck.route[-1], 0, truck.name)

    def test_status_changes_through_the_day(self):
        package = self.packages[6]  # delayed package on truck 2
        self.assertEqual(package.status_at(at("9:00")), "Delayed")
        self.assertEqual(package.status_at(at("9:05")), "En route")
        self.assertEqual(self.packages[3].status_at(at("9:00")), "At the hub")
        self.assertEqual(package.status_at(at("9:05")), "En route")
        self.assertEqual(package.status_at(package.delivered_at), "Delivered")


class DriverScheduleTest(unittest.TestCase):
    def test_truck_without_departure_waits_for_a_driver(self):
        data = load_delivery_data()
        result = run_deliveries(data)
        trucks = {t.name: t for t in result.trucks}
        self.assertEqual(trucks["Truck 3"].departs_at, min(trucks["Truck 1"].returns_at, trucks["Truck 2"].returns_at))

    def test_rejects_more_scheduled_trucks_than_drivers(self):
        data = load_delivery_data()
        for truck in data.trucks:
            truck.departs_at = at("9:05")
        with self.assertRaises(ValueError):
            run_deliveries(data)

    def test_rejects_truck_leaving_before_its_packages_arrive(self):
        data = load_delivery_data()
        data.trucks[1].departs_at = at("8:00")  # truck 2 carries the 9:05 packages
        with self.assertRaises(ValueError):
            run_deliveries(data)


class ParseClockTest(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(parse_clock("9:05"), timedelta(hours=9, minutes=5))
        self.assertEqual(parse_clock("10:30 AM"), timedelta(hours=10, minutes=30))
        self.assertEqual(parse_clock("1:15 pm"), timedelta(hours=13, minutes=15))
        self.assertEqual(parse_clock("12:00 PM"), timedelta(hours=12))
        self.assertEqual(parse_clock("12:10 AM"), timedelta(minutes=10))
        self.assertEqual(parse_clock("14:45"), timedelta(hours=14, minutes=45))

    def test_rejects_invalid_times(self):
        for text in ("", "noon", "25:00", "9:75", "9", "1:5", "+9:05", "13:00 AM", "0:30 PM"):
            with self.assertRaises(ValueError, msg=text):
                parse_clock(text)


if __name__ == "__main__":
    unittest.main()
