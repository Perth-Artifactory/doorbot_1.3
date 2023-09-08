import time
import asyncio
import logging

logger = logging.getLogger(__name__)


class MonotonicWaiter:

    def __init__(self, name: str):
        """
        Asynchronous timer using a monotonic clock.

        Allows for adjustment of wait time during waiting so it works correctly
        for asynchronous uses. Keep calling wait() and take action when it
        returns True.

        Resolution of timer is 1 second (all timing related waits are 1s long).

        name for logging.
        """
        self.name = name
        self._expiry_time = None

    def set_wait_time(self, duration_s: float):
        """
        Set or extend the wait duration in seconds. 
        """
        new_expiry_time = time.monotonic() + duration_s
        self._expiry_time = new_expiry_time

    async def wait(self) -> bool:
        """
        Waits for a short time and returns True when timer expires
        """
        if self._expiry_time:
            remaining_seconds = self._expiry_time - time.monotonic()

            if remaining_seconds <= 0:
                self._expiry_time = None
                return True
            else:
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)

        return False
