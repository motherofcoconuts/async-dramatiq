from async_dramatiq.worker import AsyncWorker
from threading import Event
import dramatiq as dq

class AsyncMiddleware(dq.Middleware):
    def before_worker_boot(self, broker: dq.Broker, worker: dq.Worker) -> None:
        startup_event = Event()
        async_worker = AsyncWorker(startup_event, broker)
        async_worker.start()
        startup_event.wait()  # Asyncio IO loop has started
        worker.workers.append(async_worker)

