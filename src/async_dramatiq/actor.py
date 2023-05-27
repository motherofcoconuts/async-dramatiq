# Standard Library Imports
import asyncio
import inspect
from datetime import timedelta
from typing import Any, Callable

import dramatiq as dq

from .scheduler import register_cron, register_interval
from .types import DramatiqWorkerPriority


class AsyncActor(dq.Actor):
    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.event_loop: asyncio.BaseEventLoop | None = None

    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """Call this function apropriately depending on its type.

        :param *args: Positional arguments to send to the actor.
        :param **kwargs: Keyword arguments to send to the actor.

        :return: Whatever the underlying function backing this actor returns.
        """
        try:
            running_event_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_event_loop = None

        if inspect.iscoroutinefunction(self.fn):
            if running_event_loop:  # Call function directly on running event loop
                result = self.fn(*args, **kwargs)
            elif (  # Run function async worker thread event loop
                self.event_loop and self.event_loop.is_running()
            ):
                future = asyncio.run_coroutine_threadsafe(
                    self.fn(*args, **kwargs), self.event_loop
                )
                result = future.result()
            else:  # This should not happen
                raise RuntimeError("No event")
        else:  # Call function directly
            result = self.fn(*args, **kwargs)

        return result

    def set_event_loop(self, loop: asyncio.BaseEventLoop | None) -> None:
        self.event_loop = loop


def async_actor(
    *,
    interval: timedelta | None = None,
    crontab: str | None = None,
    priority: DramatiqWorkerPriority = DramatiqWorkerPriority.MEDIUM,
    actor_class: type[AsyncActor] = AsyncActor,
    queue_name: str = "default",
    **kwargs: Any,
) -> Any:
    """Thin wrapper which turns a function into a dramatiq actor.

    :param interval: Run this function at a defined interval
    :param crontab: Run this function as a cron job. See https://crontab.guru/.
    :param priority: The actor's global priority.  If two tasks have
        been pulled on a worker concurrently and one has a higher
        priority than the other then it will be processed first.
        Lower numbers represent higher priorities.
    :param actor_class: The actor class to use
    :param queue_name: The name of the queue to send messages to
    :param kwargs: Input parameters for the dramatiq actor

    Dramatiq Actor: https://dramatiq.io/_modules/dramatiq/actor.html
    """

    def decorator(func: Callable[..., Any]) -> dq.Actor:
        actor = dq.actor(
            func,
            actor_class=actor_class,
            priority=priority,
            queue_name=queue_name,
            **kwargs,
        )
        if crontab:
            register_cron(actor.fn, crontab)
        if interval:
            register_interval(actor.fn, interval)

        return actor

    return decorator
