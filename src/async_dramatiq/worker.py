from __future__ import annotations

# Standard Library Imports
import asyncio
from threading import Event, Thread
import dramatiq as dq

# Local Application Imports
from baton_tms.config import config
from baton_tms.resources import shutdown, startup


class AsyncWorker(Thread):
    def __init__(self, startup_event: Event, broker: dq.broker.Broker) -> None:
        Thread.__init__(self)
        self.startup_event = startup_event
        self.broker = broker

    def run(self) -> None:
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        if not config.testing:
            self.event_loop.run_until_complete(startup())

        for actor in [  # Set event loop of actors to this loop
            self.broker.get_actor(a) for a in self.broker.get_declared_actors()
        ]:
            actor.set_event_loop(self.event_loop)

        self.event_loop.call_soon_threadsafe(self.startup_event.set)
        self.event_loop.run_forever()

        # Clean up
        if not config.testing:
            self.event_loop.run_until_complete(shutdown())
            self.event_loop.close()

    def stop(self) -> None:
        self.event_loop.call_soon_threadsafe(self.event_loop.stop)

    def pause(self) -> None:
        pass

    def resume(self) -> None:
        pass
