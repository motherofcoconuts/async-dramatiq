# Standard Library Imports
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


@dataclass
class ScheduledFunction:
    trigger: CronTrigger | IntervalTrigger
    module_path: str
    func_name: str


# Global list of scheduled jobs
scheduled_jobs: list[ScheduledFunction] = []


def _add_trigger(
    trigger: CronTrigger | IntervalTrigger, func: Callable[..., Any]
) -> None:
    global scheduled_jobs
    scheduled_jobs.append(
        ScheduledFunction(
            trigger=trigger, module_path=func.__module__, func_name=func.__name__
        )
    )


def register_cron(func: Callable[..., Any], crontab: str) -> None:
    """Register a function to be called on a cron schedule.

    :param func: The function to call.
    :param crontab: The cron schedule at which to call the function at.
        Check out https://crontab.guru/ for help.
    """
    _add_trigger(CronTrigger.from_crontab(crontab), func)


def register_interval(func: Callable[..., Any], interval: timedelta) -> None:
    """Register a function to be called on an interval.

    :param func: The function to call.
    :param interval: The interval at which to call the function at. This is a timedelta.
    """
    _add_trigger(IntervalTrigger(seconds=interval.total_seconds()), func)
