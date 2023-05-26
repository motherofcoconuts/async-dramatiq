from __future__ import annotations

# Standard Library Imports
import asyncio
import inspect
from datetime import timedelta
from typing import Any, Callable

import dramatiq as dq

# from baton_tms.helpers.monitoring import monitor
# from sentry_sdk import start_transaction

from .scheduler import register_cron, register_interval
from .types import DramatiqWorkerPriority


class AsyncActor(dq.Actor):
    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.event_loop: asyncio.BaseEventLoop | None = None

    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """Synchronously call this actor.

        :param *args: Positional arguments to send to the actor.
        :param **kwargs: Keyword arguments to send to the actor.

        :return: Whatever the underlying function backing this actor returns.
        """
        try:
            running_event_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_event_loop = None

        # with start_transaction(op="actor", name=self.actor_name):
        if inspect.iscoroutinefunction(self.fn):
            if running_event_loop:  # Call function directly
                result = self.fn(*args, **kwargs)
            elif (  # Call function through worker thread
                self.event_loop and self.event_loop.is_running()
            ):
                future = asyncio.run_coroutine_threadsafe(
                    self.fn(*args, **kwargs), self.event_loop
                )
                result = future.result()
            else:  # This should not happen
                raise RuntimeError("No event")
        else:
            result = self.fn(*args, **kwargs)
        return result

    def set_event_loop(self, loop: asyncio.BaseEventLoop | None) -> None:
        self.event_loop = loop


def dramatiq_actor(
    *,
    interval: timedelta | None = None,
    crontab: str | None = None,
    monitor_id: str | None = None,
    priority: DramatiqWorkerPriority = DramatiqWorkerPriority.MEDIUM,
    **kwargs: Any,
) -> Any:
    """Thin wrapper which turns a function into a dramatiq actor.

    :param interval: Run this function at a defined interval
    :param crontab: Run this function as a cron job
    :param monitor_id: The Sentry `monitor_id` for this job
    :param priority: The actor's global priority.  If two tasks have
        been pulled on a worker concurrently and one has a higher
        priority than the other then it will be processed first.
        Lower numbers represent higher priorities.
    :param kwargs: Input parameters for the dramatiq actor

    Dramatiq Actor: https://dramatiq.io/_modules/dramatiq/actor.html
    """
    def decorator(func: Callable[..., Any]) -> dq.Actor:
        if interval or crontab:
            queue_name = kwargs.get("queue_name") or "default"
            throws: tuple[Exception, ...] = kwargs.get("throws", ())
            # func = monitor(
            #     func,
            #     name=f"{func.__name__} from {queue_name}",
            #     monitor_id=monitor_id,
            #     throws=throws,
            # )
        actor = dq.actor(func, actor_class=AsyncActor, priority=priority, **kwargs)
        if crontab:
            register_cron(actor.fn, crontab)
        if interval:
            register_interval(actor.fn, interval)

        return actor

    return decorator
