# Standard Library Imports
from threading import Event

from dramatiq.brokers.stub import StubBroker

# Local Application Imports
from async_dramatiq.worker import AsyncWorker


def test_async_worker(broker: StubBroker) -> None:
    startup_event = Event()
    async_worker = AsyncWorker(startup_event, broker)
    async_worker.start()
    startup_event.wait()  # Asyncio IO loop has started

    assert async_worker.event_loop.is_running()

    async_worker.stop()
    async_worker.join()

    assert not async_worker.event_loop.is_running()

    async_worker.pause()
    async_worker.resume()
