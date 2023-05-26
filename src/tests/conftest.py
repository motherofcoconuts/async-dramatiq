from typing import Generator
import pytest
from dramatiq import Broker, Worker
from dramatiq.brokers.stub import StubBroker
from async_dramatiq import get_backend, get_broker, set_backend, set_broker
from async_dramatiq.backends import AsyncStubBackend
from async_dramatiq.middleware import AsyncMiddleware, StubAsyncMiddleware


@pytest.fixture(scope="module")
def stub_broker() -> Worker:
    broker = StubBroker()
    set_broker(broker)
    yield broker


@pytest.fixture(scope="module")
def broker() -> Worker:
    broker = Broker()
    set_broker(broker)

    yield broker


@pytest.fixture(scope="module")
def worker(stub_broker) -> Worker:
    worker = Worker(stub_broker, worker_timeout=100, worker_threads=2)
    worker.start()

    yield worker

    worker.stop()
    worker.join()


@pytest.fixture(scope="module")
def worker_thread(broker) -> Worker:
    worker = Worker(broker, worker_timeout=100, worker_threads=2)
    worker.start()

    yield worker

    worker.stop()
    worker.join()
