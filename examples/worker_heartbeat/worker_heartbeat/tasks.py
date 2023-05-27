# Standard Library Imports
import asyncio
import logging
import time
from datetime import timedelta

from .worker import bg_task


@bg_task(store_results=True, interval=timedelta(seconds=5))
def worker_heartbeat() -> float:
    t = time.time()
    logging.info(f"Worker Heartbeat @ {t}")

    return t


@bg_task(store_results=True)
async def worker_sleep(sleep_for: float) -> float:
    logging.info("Worker Slepping for {sleep_for} seconds")
    await asyncio.sleep(sleep_for)
    logging.info("Worker is awake")

    return sleep_for
