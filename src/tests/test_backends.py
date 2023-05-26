# Standard Library Imports
import time
from threading import Thread

import pytest
from dramatiq import Message
from dramatiq.actor import actor
from dramatiq.results.backend import ResultMissing, ResultTimeout

# Local Application Imports
from baton_tms.config import config
from async_dramatiq.backends import AsyncRedisBackend, AsyncStubBackend


def get_message() -> Message:
    @actor(queue_name="test_queue", store_results=True)
    def my_func():
        pass

    return my_func.message()


async def assert_result(backend, msg, result, timeout=3000):
    returned_result = await backend.get_result(msg, block=True, timeout=timeout)
    assert returned_result == result


def delayed_store(backend, msg, result, ttl):
    time.sleep(2)
    backend.store_result(message=msg, result=result, ttl=ttl)


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(**config.redis_params), AsyncStubBackend()]
)
async def test_get_result_happy_path(redis, backend, session):
    msg = get_message()
    result = "this is a result"

    backend.store_result(message=msg, result=result, ttl=100000)
    returned_result = await backend.get_result(msg)
    assert returned_result == result


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(**config.redis_params), AsyncStubBackend()]
)
async def test_get_result_result_missing(redis, backend):
    msg = get_message()

    with pytest.raises(ResultMissing):
        await backend.get_result(msg)


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(**config.redis_params), AsyncStubBackend()]
)
async def test_get_result_blocking_happy_path(redis, backend, session):
    msg = get_message()
    result = "this is a result"

    t1 = Thread(target=delayed_store, args=[backend, msg, result, 5000])
    t1.start()

    await assert_result(backend, msg, result)

    t1.join()


@pytest.mark.parametrize(
    "backend", [AsyncRedisBackend(**config.redis_params), AsyncStubBackend()]
)
async def test_get_result_blocking_timeout(redis, backend):
    msg = get_message()
    result = "this is a result"

    t1 = Thread(target=delayed_store, args=[backend, msg, result, 10000])
    t1.start()

    with pytest.raises(ResultTimeout):
        await assert_result(backend, msg, result, 0)

    t1.join()
