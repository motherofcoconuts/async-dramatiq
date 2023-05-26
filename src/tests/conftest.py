# Standard Library Imports
import asyncio
from typing import Generator

import pytest
import redis
from dramatiq import Worker
from dramatiq.brokers.stub import StubBroker

# Local Application Imports
from async_dramatiq import set_broker
from async_dramatiq.backends import AsyncRedisBackend, AsyncStubBackend, set_backend
from async_dramatiq.middleware import AsyncMiddleware


def check_redis(client: redis.Redis) -> None:
    try:
        client.ping()
    except redis.ConnectionError as e:
        raise e


@pytest.fixture
def event_loop() -> Generator[asyncio.BaseEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def broker() -> Generator[StubBroker, None, None]:
    broker = StubBroker()
    set_broker(broker)
    yield broker


@pytest.fixture
def async_stub_backend() -> Generator[AsyncStubBackend, None, None]:
    backend = AsyncStubBackend()
    set_backend(backend)
    yield backend


@pytest.fixture
def async_redis_result_backend() -> Generator[AsyncRedisBackend, None, None]:
    backend = AsyncRedisBackend()
    check_redis(backend.client)
    backend.client.flushall()
    yield backend
    backend.client.flushall()


@pytest.fixture
def worker(broker: StubBroker) -> Worker:
    broker.add_middleware(AsyncMiddleware())
    worker = Worker(broker, worker_timeout=100, worker_threads=2)
    worker.start()

    yield worker

    worker.stop()
    worker.join()
