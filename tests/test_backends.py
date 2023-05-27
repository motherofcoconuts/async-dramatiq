# Standard Library Imports
import os
import time
from threading import Thread

import pytest
from dramatiq import Message
from dramatiq.actor import actor
from dramatiq.results.backend import ResultMissing, ResultTimeout

# Local Application Imports
from async_dramatiq.backends import AsyncRedisBackend, AsyncStubBackend, set_backend

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)


def get_message() -> Message:
    @actor(queue_name="test_queue", store_results=True)
    def my_func():
        pass

    return my_func.message()


async def assert_result(
    backend: AsyncRedisBackend | AsyncStubBackend,
    msg: Message,
    result: str,
    timeout: int = 3000,
) -> None:
    returned_result = await backend.get_result(msg, block=True, timeout=timeout)
    assert returned_result == result


def delayed_store(
    backend: AsyncRedisBackend | AsyncStubBackend, msg: Message, result: str, ttl: int
) -> None:
    time.sleep(0.1)
    backend.store_result(message=msg, result=result, ttl=ttl)


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(host=REDIS_HOST, port=REDIS_PORT), AsyncStubBackend()]
)
async def test_get_result_happy_path(
    backend: AsyncRedisBackend | AsyncStubBackend,
) -> None:
    set_backend(backend)

    msg = get_message()
    result = "this is a result"
    backend.store_result(message=msg, result=result, ttl=100000)
    returned_result = await backend.get_result(msg)
    assert returned_result == result


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(host=REDIS_HOST, port=REDIS_PORT), AsyncStubBackend()]
)
async def test_get_result_result_missing(
    backend: AsyncRedisBackend | AsyncStubBackend,
) -> None:
    set_backend(backend)

    msg = get_message()

    with pytest.raises(ResultMissing):
        await backend.get_result(msg)


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(host=REDIS_HOST, port=REDIS_PORT), AsyncStubBackend()]
)
async def test_get_result_blocking_happy_path(
    backend: AsyncRedisBackend | AsyncStubBackend,
) -> None:
    set_backend(backend)

    msg = get_message()
    result = "this is a result"

    t1 = Thread(target=delayed_store, args=[backend, msg, result, 5000])
    t1.start()

    await assert_result(backend, msg, result)

    t1.join()


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(host=REDIS_HOST, port=REDIS_PORT), AsyncStubBackend()]
)
async def test_get_result_blocking_timeout(
    backend: AsyncRedisBackend | AsyncStubBackend,
) -> None:
    set_backend(backend)

    msg = get_message()
    result = "this is a result"

    t1 = Thread(target=delayed_store, args=[backend, msg, result, 10000])
    t1.start()

    with pytest.raises(ResultTimeout):
        await assert_result(backend, msg, result, 0)

    t1.join()
