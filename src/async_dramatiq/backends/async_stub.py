# Standard Library Imports
import asyncio
import time

import dramatiq as dq
from dramatiq.results.backend import (
    Missing,
    Result,
    ResultMissing,
    ResultTimeout,
    compute_backoff,
)
from dramatiq.results.backends import StubBackend

from async_dramatiq.config import DEFAULT_TIMEOUT, BACKOFF_FACTOR

class AsyncStubBackend(StubBackend):
    async def get_result(
        self, message: dq.Message, *, block: bool = False, timeout: int | None = None
    ) -> Result:
        """Get a result from the backend.
        Sub-second timeouts are not respected by this backend.

        :param message: The dramatiq message object
        :param block: Whether or not to block until a result is set.
        :param timeout: The maximum amount of time, in ms, to wait for
          a result when block is True.  Defaults to 10 seconds.

        :raise ResultMissing: When block is False and the result isn't set.
        :raise ResultTimeout: When waiting for a result times out.

        :return: The result object.
        """
        if timeout is None:
            timeout = DEFAULT_TIMEOUT

        end_time = time.monotonic() + timeout / 1000
        message_key = self.build_message_key(message)

        attempts = 0
        while True:
            result = self._get(message_key)
            if result is Missing and block:
                attempts, delay = compute_backoff(attempts, factor=BACKOFF_FACTOR)
                delay /= 1000
                if time.monotonic() + delay > end_time:
                    raise ResultTimeout(message)

                await asyncio.sleep(delay)
                continue

            elif result is Missing:
                raise ResultMissing(message)

            else:
                return self.unwrap_result(result)
