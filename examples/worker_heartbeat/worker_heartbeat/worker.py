# Standard Library Imports
import logging
from functools import partial
from typing import Any

import worker_heartbeat.config as config
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.brokers.stub import StubBroker

# Local Application Imports
import async_dramatiq as adtq
from async_dramatiq.actors import async_actor
from async_dramatiq.backends import AsyncRedisBackend, AsyncStubBackend
from async_dramatiq.middleware import AsyncMiddleware, StubAsyncMiddleware
from async_dramatiq.types import DramatiqWorkerPriority, TaskQueue
from async_dramatiq.worker import AsyncWorker

# Declare the queues
bg_queue = TaskQueue(queue="bg_tasks")
queues = {bg_queue.queue: bg_queue}

# Decorator for background tasks
bg_task = partial(
    async_actor, priority=DramatiqWorkerPriority.HIGH, queue_name=bg_queue.queue
)


async def startup() -> None:
    """This function should contain your resource initialization code."""
    logging.info("Starting up")


async def shutdown() -> None:
    """This function should contain your resource teardown code."""
    logging.info("Shutting down")


class MyAsyncMiddleware(AsyncMiddleware):
    def before_async_worker_thread_startup(
        self, _: RabbitmqBroker, thread: AsyncWorker, **kwargs: dict[str, Any]
    ) -> None:
        thread.event_loop.run_until_complete(startup())

    def after_async_worker_thread_shutdown(
        self, _: RabbitmqBroker, thread: AsyncWorker, **kwargs: dict[str, Any]
    ) -> None:
        thread.event_loop.run_until_complete(shutdown())
        thread.event_loop.close()


def configure() -> None:
    # Configure Backend and Broker
    if config.testing:
        broker = StubBroker()
        backend = AsyncStubBackend()
        logging.info("Testing")
    else:
        broker = RabbitmqBroker(
            host=config.broker_host,
            port=config.broker_port,
            credentials=config.broker_credentials,
        )
        backend = AsyncRedisBackend(host=config.redis_host, port=config.redis_port)
        logging.info(f"Broker: {config.broker_host}:{config.broker_port}")
        logging.info(f"Backend: {config.redis_host}:{config.redis_port}")

    adtq.set_broker(broker)
    adtq.set_backend(backend)

    # Setup Middleware
    if config.testing:
        adtq.get_broker().add_middleware(StubAsyncMiddleware())
    else:
        adtq.get_broker().add_middleware(MyAsyncMiddleware())

    # Setup Queues
    for queue_name in queues.keys():
        kwargs = {"ensure": True} if not config.testing else {}
        adtq.get_broker().declare_queue(queue_name, **kwargs)
        logging.info(f"Declared queue: {queue_name}")

    logging.info("Configured Dramatiq")


configure()
