# Dramatiq with Asyncio
[Dramatiq](https://dramatiq.io/) is a background task processing library for Python with a focus on simplicity, reliability and performance.

This package extends dramatiq to provide the following:
  1. Support for Asyncio ( [issue #238](https://github.com/Bogdanp/dramatiq/issues/238) )
  2. Message scheduling support ( [scheduling cookbook](https://dramatiq.io/cookbook.html#scheduling-messages) )

### Getting Started
The quickest way to get started is by playing around with the [worker heartbeat example](examples/worker_heartbeat/README.md).

# The Code
## Async Middleware
### Broker
To provide async support for your actors all you need to do is add the `AsyncMiddleware` to your broker.
#### RabbitMQ Broker

```
import dramatiq

from dramatiq.brokers.rabbitmq import RabbitmqBroker


rabbitmq_broker = RabbitmqBroker(host="rabbitmq")
rabbitmq_broker.add_middleware(AsyncMiddleware())  # <--- Here
dramatiq.set_broker(rabbitmq_broker)
```

#### Redis Broker

```
import dramatiq
import dramatiq

from dramatiq.brokers.redis import RedisBroker


redis_broker = RedisBroker(host="redis")
redis_broker.add_middleware(AsyncMiddleware()) # <--- Here
dramatiq.set_broker(redis_broker)
```

### Startup and Shutdown Events
To startup and shutdown any resources the `AsyncMiddleware` provides two hooks:
1. Before the event loop is started
2. After the event loop is stopped
To allow for standing up or tearing down of shared async resources
#### Example
```
from async_dramatiq.middleware import AsyncMiddleware

async def startup() -> None:
    """This function should contain your resource initialization code."""
    pass

async def shutdown() -> None:
    """This function should contain your resource teardown code."""
    pass


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
```

## Async Actor
The async actor, `async_dramatiq_actor`,  acts as a thin wrapper around the dramatiq actor providing a variety of new functionality.

#### Interval Jobs
Run a job at some interval
```
@async_dramatiq_actor(interval=timedelta(seconds=5))
def run_every_5_seconds() -> None:
    pass
```

#### Cron Jobs
Run a job on a crontab ( See https://crontab.guru/. )
```
@async_dramatiq_actor(interval="0 0 * * *")
def run_at_midnight() -> None:
  pass
```

## Running
### The Scheduler
Checkout [run_scheduler.py](examples/worker_heartbeat/run_scheduler.py) for an example on running the scheduler.
### Dramatiq Worker
Check out the offical guide [dramatiq](https://dramatiq.io/guide.html#workers)

