# Standard Library Imports
import asyncio

import click
from worker_heartbeat.tasks import async_worker_sleep, worker_heartbeat

# Local Application Imports
import async_dramatiq as adtq


async def heartbeat() -> None:
    msg = worker_heartbeat.send()
    print(f"Sending heartbeat task {msg}...")
    result = await adtq.get_backend().get_result(msg, block=True)
    print(f"Worker heartbeat @ {result}")


async def sleep(sleep_for: float) -> None:
    msg = async_worker_sleep.send(sleep_for)
    print(f"Sending sleep task {msg}...")
    result = await adtq.get_backend().get_result(msg, block=True)
    print(f"Worker slept for {result} seconds")


@click.command()
@click.option("--send_heartbeat", is_flag=True, help="Send a heartbeat")
@click.option("--sleep_for", default=0, type=float, help="Sleep for N seconds")
def run(send_heartbeat: bool, sleep_for: float) -> None:
    """Test Async Dramatiq Functionality"""
    loop = asyncio.get_event_loop()
    if send_heartbeat:
        loop.run_until_complete(heartbeat())
    elif sleep_for > 0:
        loop.run_until_complete(sleep(sleep_for))
    loop.close()


if __name__ == "__main__":
    run()
