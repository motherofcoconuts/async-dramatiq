# Standard Library Imports
from datetime import timedelta
from typing import Any, Callable

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel


class ScheduledFunction(BaseModel):
    trigger: CronTrigger | IntervalTrigger
    module_path: str
    func_name: str

    class Config:
        arbitrary_types_allowed = True


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
    _add_trigger(CronTrigger.from_crontab(crontab), func)


def register_interval(func: Callable[..., Any], interval: timedelta) -> None:
    _add_trigger(IntervalTrigger(seconds=interval.total_seconds()), func)