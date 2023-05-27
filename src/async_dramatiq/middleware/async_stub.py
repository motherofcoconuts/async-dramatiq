# Standard Library Imports
import asyncio

import dramatiq as dq


class StubAsyncMiddleware(dq.Middleware):
    """Stub middleware that sets the event loop of actors to the current loop.
    This is used for testing. Standard use case would be to add the following
    fixture in your conftest.py:

        @pytest.fixture(scope="session")
        def event_loop() -> Generator[asyncio.BaseEventLoop, None, None]:
            loop = asyncio.get_event_loop_policy().new_event_loop()
            yield loop
            loop.close()
    """

    event_loop: asyncio.BaseEventLoop

    def before_worker_boot(self, broker: dq.Broker, worker: dq.Worker) -> None:
        event_loop = asyncio.get_event_loop()
        for actor in [  # Set event loop of actors to this loop
            broker.get_actor(a) for a in broker.get_declared_actors()
        ]:
            actor.set_event_loop(event_loop)

    def before_worker_shutdown(self, broker: dq.Broker, _: dq.Worker) -> None:
        for actor in [  # Set event loop of actors to this loop
            broker.get_actor(a) for a in broker.get_declared_actors()
        ]:
            actor.set_event_loop(None)
