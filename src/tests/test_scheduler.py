# Standard Library Imports
from datetime import timedelta

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Local Application Imports
from async_dramatiq.scheduler import register_cron, register_interval
from async_dramatiq.scheduler import scheduled_jobs


def test_register_jobs() -> None:
    def test_func() -> None:
        return None

    crontab = "* * * * *"
    register_cron(test_func, crontab)
    assert isinstance(scheduled_jobs[-1].trigger, CronTrigger)
    assert scheduled_jobs[-1].module_path == test_func.__module__
    assert scheduled_jobs[-1].func_name == test_func.__name__


def test_register_interval() -> None:
    def test_func() -> None:
        return None

    interval = timedelta(seconds=60)
    register_interval(test_func, interval)
    assert isinstance(scheduled_jobs[-1].trigger, IntervalTrigger)
    assert scheduled_jobs[-1].module_path == test_func.__module__
    assert scheduled_jobs[-1].func_name == test_func.__name__
