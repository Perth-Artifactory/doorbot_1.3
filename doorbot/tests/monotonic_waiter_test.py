import unittest
from unittest.mock import patch, MagicMock, call
from doorbot.interfaces.monotonic_waiter import MonotonicWaiter
import asyncio

class TestMonotonicWaiter(unittest.TestCase):

    def setUp(self):
        self.monotonic_mock = MagicMock()
        self.monotonic_mock.side_effect = self._mocked_monotonic()
        self._mocked_time = 0

    def _mocked_monotonic(self):
        while True:
            yield self._mocked_time

    def mocked_sleep(self, seconds):
        self._mocked_time += seconds

    def test_no_expiry_time(self):
        waiter = MonotonicWaiter("TestWaiter")
        result = asyncio.run(waiter.wait())
        self.assertFalse(result)

    def test_wait_time_expired(self):
        with patch("time.monotonic", self.monotonic_mock):
            waiter = MonotonicWaiter("TestWaiter")
            waiter.set_wait_time(5)
            self._mocked_time += 6
            result = asyncio.run(waiter.wait())
            self.assertTrue(result)

    def test_wait_time_not_expired(self):
        with patch("time.monotonic", self.monotonic_mock):
            with patch("asyncio.sleep", side_effect=self.mocked_sleep):
                waiter = MonotonicWaiter("TestWaiter")
                waiter.set_wait_time(5)
                self._mocked_time += 3
                result = asyncio.run(waiter.wait())
                self.assertFalse(result)

    def test_allow_wait_time_change(self):
        with patch("time.monotonic", self.monotonic_mock):
            waiter = MonotonicWaiter("TestWaiter")
            waiter.set_wait_time(5)
            self._mocked_time += 2
            waiter.set_wait_time(1)  # New time should override the previous setting
            self._mocked_time += 1.5
            result = asyncio.run(waiter.wait())
            self.assertTrue(result)

    def test_multiple_wait_before_expiry(self):
        with patch("time.monotonic", self.monotonic_mock):
            with patch("asyncio.sleep", side_effect=self.mocked_sleep):
                waiter = MonotonicWaiter("TestWaiter")
                waiter.set_wait_time(5)
                for _ in range(4):
                    result = asyncio.run(waiter.wait())
                    self.assertFalse(result)
                self._mocked_time += 4.5
                result = asyncio.run(waiter.wait())
                self.assertTrue(result)

    def test_without_setting_wait_time(self):
        with patch("time.monotonic", self.monotonic_mock):
            waiter = MonotonicWaiter("TestWaiter")
            result = asyncio.run(waiter.wait())
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
