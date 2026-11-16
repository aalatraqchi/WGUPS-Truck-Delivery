import io
import unittest
from contextlib import redirect_stdout
from datetime import timedelta
from unittest import mock

from wgups import cli


def run(argv, stdin=""):
    lines = iter(stdin.splitlines())

    def fake_input(prompt=""):
        try:
            return next(lines)
        except StopIteration:
            raise EOFError from None

    output = io.StringIO()
    with redirect_stdout(output), mock.patch("builtins.input", fake_input):
        cli.main(argv)
    return output.getvalue()


class FormatClockTest(unittest.TestCase):
    def test_formats_and_rounds_up(self):
        self.assertEqual(cli.format_clock(timedelta(hours=9, minutes=5)), "9:05 AM")
        self.assertEqual(cli.format_clock(timedelta(hours=12, minutes=0)), "12:00 PM")
        self.assertEqual(cli.format_clock(timedelta(hours=13, minutes=4, seconds=1)), "1:05 PM")
        self.assertEqual(cli.format_clock(timedelta(minutes=30)), "12:30 AM")


class CliTest(unittest.TestCase):
    def test_snapshot_of_all_packages(self):
        output = run(["--time", "10:30"])
        self.assertIn("All 40 packages delivered", output)
        self.assertIn("Status of all packages at 10:30 AM", output)
        self.assertEqual(output.count("Truck 1  Delivered at"), 16)

    def test_snapshot_of_one_package_shows_address_known_at_that_time(self):
        self.assertIn("300 State St", run(["--time", "10:00", "--package", "9"]))
        self.assertIn("410 S State St", run(["--time", "10:20", "--package", "9"]))

    def test_unknown_package_is_an_error_before_any_output(self):
        output = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stdout(output), mock.patch("sys.stderr", io.StringIO()):
            cli.main(["--time", "10:00", "--package", "99"])
        self.assertEqual(output.getvalue(), "")

    def test_delayed_package_status_before_its_flight_lands(self):
        self.assertIn("Delayed, arrives 9:05 AM", run(["--time", "8:30", "--package", "6"]))

    def test_menu_exits_cleanly_at_end_of_input(self):
        self.assertIn("Choose an option", run([], stdin="1\n"))

    def test_interactive_menu(self):
        output = run([], stdin="2\n99\n²\n15\nlater\n9:00 AM\n3\n4\n")
        self.assertIn("No package with ID '99' was found.", output)
        self.assertIn("No package with ID '²' was found.", output)
        self.assertIn("That isn't a valid time.", output)
        self.assertIn("Status of package 15 at 9:00 AM", output)
        self.assertIn("Delivered at 8:13 AM", output)


if __name__ == "__main__":
    unittest.main()
