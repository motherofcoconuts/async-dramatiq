# Standard Library Imports
import threading
from threading import Event
from typing import Any

import dramatiq as dq

# Local Application Imports
from async_dramatiq.worker import AsyncWorker

lock = threading.Lock()
is_initialized = False


class AsyncMiddleware(dq.Middleware):
    """Middleware that runs the Asyncio Event Loop in a separate worker."""

    def before_worker_boot(self, broker: dq.Broker, worker: dq.Worker) -> None:
        global lock, is_initialized

        if lock.acquire(blocking=False):
            if not is_initialized:
                startup_event = Event()
                async_worker = AsyncWorker(startup_event, broker)
                async_worker.start()
                startup_event.wait()  # Wait until the Asyncio Event Loop has started
                worker.workers.append(async_worker)
                is_initialized = True
            else:
                raise RuntimeError(
                    "AsyncWorker already initialized with an event loop."
                )
            lock.release()

    def before_async_worker_thread_startup(
        self, broker: dq.Broker, thread: AsyncWorker, **kwargs: dict[str, Any]  # noqa
    ) -> None:
        pass

    def after_async_worker_thread_shutdown(
        self, broker: dq.Broker, thread: AsyncWorker, **kwargs: dict[str, Any]  # noqa
    ) -> None:
        pass
