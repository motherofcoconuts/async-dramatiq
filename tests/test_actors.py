# Standard Library Imports
import asyncio
from datetime import timedelta

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from dramatiq import Worker

# Local Application Imports
from async_dramatiq.actors import dramatiq_actor
from async_dramatiq.backends import AsyncStubBackend, get_backend
from async_dramatiq.scheduler import scheduled_jobs


def test_dramatiq_actor() -> None:
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


async def test_async_actor_func(event_loop: asyncio.BaseEventLoop) -> None:
    result = "generic result"

    @dramatiq_actor()
    async def test_async():
        return result

    # Test generic run
    assert result == await test_async()


def test_async_actor_func_no_loop() -> None:
    result = "generic result"

    @dramatiq_actor()
    async def test_async():
        return result

    # Test generic run
    with pytest.raises(RuntimeError):
        test_async()


async def test_async_actor_func_in_thread(
    worker: Worker, async_stub_backend: AsyncStubBackend
) -> None:
    result = "generic result"

    @dramatiq_actor(store_results=True)
    async def test_async():
        return result

    # Setup actor event loop
    loop = (w.event_loop for w in worker.workers if hasattr(w, "event_loop"))
    test_async.event_loop = next(loop, None)

    # Send actor to worker
    msg = test_async.send()
    worker.join()

    return_result = await get_backend().get_result(msg, block=True)
    assert return_result == result


async def test_sync_actor_func() -> None:
    result = "generic result"

    @dramatiq_actor()
    def test_sync():
        return result

    assert result == test_sync()


def test_sync_actor_func_no_loop() -> None:
    result = "generic result"

    @dramatiq_actor()
    def test_sync():
        return result

    assert result == test_sync()


async def test_sync_actor_func_in_thread(
    worker: Worker, async_stub_backend: AsyncStubBackend
) -> None:
    result = "generic result"

    @dramatiq_actor(store_results=True)
    def test_async():
        return result

    # Send actor to worker
    msg = test_async.send()
    worker.join()

    return_result = await get_backend().get_result(msg, block=True)

    assert return_result == result


async def test_async_request(
    worker: Worker, async_stub_backend: AsyncStubBackend
) -> None:
    @dramatiq_actor(store_results=True)
    async def test_async():
        await asyncio.sleep(0.25)
        return True

    # Setup actor event loop
    loop = (w.event_loop for w in worker.workers if hasattr(w, "event_loop"))
    test_async.event_loop = next(loop, None)

    # Send actor to worker
    msg = test_async.send()
    worker.join()

    assert await get_backend().get_result(msg, block=True) is True

    # Send actor to worker
    msg = test_async.send()
    worker.join()

    assert await get_backend().get_result(msg, block=True) is True
