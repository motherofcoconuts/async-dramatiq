import dramatiq as dq
from dramatiq.results.backend import (
    DEFAULT_TIMEOUT,
    Result,
    ResultMissing,
    ResultTimeout,
)
from dramatiq.results.backends.redis import RedisBackend


class AsyncRedisBackend(RedisBackend):
    """A Redis backend that supports async redis client.

    TODO: Use async redis client instead of sync client
    """

    async def get_result(
        self, message: dq.Message, *, block: bool = False, timeout: int | None = None
    ) -> Result:
        """Get a result from the backend. Sub-second timeouts are not respected by
        this backend.

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

        message_key = self.build_message_key(message)
        if block:
            timeout = int(timeout / 1000)
            if timeout == 0:
                data = self.client.rpoplpush(message_key, message_key)
            else:
                data = self.client.brpoplpush(message_key, message_key, timeout)

            if data is None:
                raise ResultTimeout(message)

        else:
            data = self.client.lindex(message_key, 0)
            if data is None:
                raise ResultMissing(message)

        return self.unwrap_result(self.encoder.decode(data))
