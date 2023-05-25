from __future__ import annotations

# Standard Library Imports
from dataclasses import dataclass
from enum import IntEnum
from functools import partial

import dramatiq
from dramatiq.broker import Broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.brokers.stub import StubBroker
from dramatiq.results import Results
from dramatiq.results.backend import ResultBackend
from loguru import logger

# Local Application Imports
from baton_tms.config import config
from baton_tms.tasks.core.actors import dramatiq_actor
from baton_tms.tasks.core.backends import AsyncRedisBackend, AsyncStubBackend
from baton_tms.tasks.core.middleware import AsyncMiddleware, StubAsyncMiddleware

from .logger import configure_logger


class DramatiqWorkerPriority(IntEnum):
    CRITICAL = 0
    VERY_HIGH = 1
    HIGH = 3
    MEDIUM = 4
    LOW = 5
    VERY_LOW = 6


@dataclass
class TaskQueue:
    queue: str
    message_ttl: int | None = 60 * 60  # Max time a task can sit in the queue



def create_backend(*, stubbed: bool = False) -> ResultBackend:
    if stubbed:
        backend = AsyncStubBackend()
    else:
        backend = AsyncRedisBackend(**config.redis_params)
        logger.info(f"Connected Redis Backend: {config.redis_host}:{config.redis_port}")

    logger.info("Configured Results Backend")

    return backend


def create_broker(
    backend: ResultBackend,
    queues: dict[str, TaskQueue],
    *,
    stub_broker: bool = False,
    stub_middleware: bool = False,
) -> Broker:
    if stub_broker:
        broker = StubBroker()
    else:
        broker = RabbitmqBroker(
            # virtual_host=config.broker_vhost,
            host=config.broker_host,
            port=config.broker_port,
            credentials=config.pika_credentials,
        )
        logger.info(
            f"Connected Rabbitmq Broker: {config.broker_host}:{config.broker_port}"
        )

    dramatiq.set_broker(broker)
    configure_middleware(broker, backend, use_stub=stub_middleware)
    configure_queues(broker, queues)

    logger.info("Configured Broker")

    return broker


def configure_middleware(
    broker: Broker, backend: ResultBackend, *, use_stub: bool = False
) -> None:
    broker.add_middleware(Results(backend=backend))
    if use_stub:
        broker.add_middleware(StubAsyncMiddleware())
    else:
        broker.add_middleware(AsyncMiddleware())


def configure_queues(broker: Broker, queues: dict[str, TaskQueue]) -> None:
    for queue_name in queues.keys():
        kwargs = {"ensure": True} if not config.testing else {}
        broker.declare_queue(queue_name, **kwargs)

