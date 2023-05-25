import asyncio
import dramatiq as dq
from async_dramatiq.config import TESTING

class StubAsyncMiddleware(dq.Middleware):
    event_loop: asyncio.BaseEventLoop

    def before_worker_boot(self, broker: dq.Broker, worker: dq.Worker) -> None:
        event_loop = asyncio.get_event_loop()
        for actor in [  # Set event loop of actors to this loop
            broker.get_actor(a) for a in broker.get_declared_actors()
        ]:
            actor.set_event_loop(event_loop)

    def before_worker_shutdown(self, broker: dq.Broker, _: dq.Worker) -> None:
        if TESTING:
            for actor in [  # Set event loop of actors to this loop
                broker.get_actor(a) for a in broker.get_declared_actors()
            ]:
                actor.set_event_loop(None)
