# Standard Library Imports
from datetime import timedelta

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Local Application Imports
from async_dramatiq.actors import dramatiq_actor
from async_dramatiq.backends import get_backend
from async_dramatiq.scheduler import scheduled_jobs


def test_dramatiq_actor():
    scheduled_jobs_len = len(scheduled_jobs)

    @dramatiq_actor(interval=timedelta(seconds=5))
    def test_interval():
        return None

    @dramatiq_actor(crontab="* * * * *")
    def test_cron():
        return None

    @dramatiq_actor()
    async def test_async():
        return None

    assert len(scheduled_jobs) == scheduled_jobs_len + 2
    assert isinstance(scheduled_jobs[-1].trigger, CronTrigger)
    assert scheduled_jobs[-1].module_path, test_cron.__module__
    assert scheduled_jobs[-1].func_name, test_cron.__name__

    assert isinstance(scheduled_jobs[-2].trigger, IntervalTrigger)
    assert scheduled_jobs[-2].module_path, test_interval.__module__
    assert scheduled_jobs[-2].func_name, test_interval.__name__


async def test_async_actor_func(event_loop):
    result = "generic result"

    @dramatiq_actor()
    async def test_async():
        return result

    # Test generic run
    assert result == await test_async()


def test_async_actor_func_no_loop():
    result = "generic result"

    @dramatiq_actor()
    async def test_async():
        return result

    # Test generic run
    with pytest.raises(RuntimeError):
        test_async()


async def test_async_actor_func_in_thread(worker_thread):
    result = "generic result"

    @dramatiq_actor(store_results=True)
    async def test_async():
        return result

    # Setup actor event loop
    loop = (w.event_loop for w in worker_thread.workers if hasattr(w, "event_loop"))
    test_async.event_loop = next(loop, None)

    # Send actor to worker
    msg = test_async.send()
    worker_thread.join()

    return_result = await get_backend().get_result(msg, block=True)
    assert return_result == result


async def test_sync_actor_func():
    result = "generic result"

    @dramatiq_actor()
    def test_sync():
        return result

    assert result == test_sync()


def test_sync_actor_func_no_loop():
    result = "generic result"

    @dramatiq_actor()
    def test_sync():
        return result

    assert result == test_sync()


async def test_sync_actor_func_in_thread(worker_thread):
    result = "generic result"

    @dramatiq_actor(store_results=True)
    def test_async():
        return result

    # Send actor to worker
    msg = test_async.send()
    worker_thread.join()

    return_result = await get_backend().get_result(msg, block=True)

    assert return_result == result


async def test_async_request(worker_thread):
    @dramatiq_actor(store_results=True)
    async def test_async():
        from baton_tms.resources import http_client

        await http_client.get("https://www.google.com", timeout=5)

        return True

    # Setup actor event loop
    loop = (w.event_loop for w in worker_thread.workers if hasattr(w, "event_loop"))
    test_async.event_loop = next(loop, None)

    # Send actor to worker
    msg = test_async.send()
    worker_thread.join()

    assert await get_backend().get_result(msg, block=True) == True

    # Send actor to worker
    msg = test_async.send()
    worker_thread.join()

    assert await get_backend().get_result(msg, block=True) == True
