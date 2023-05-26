from dramatiq import get_broker
from dramatiq.results import Results
from dramatiq.results.backend import ResultBackend

from .async_redis import AsyncRedisBackend  # noqa: F401
from .async_stub import AsyncStubBackend  # noqa: F401

backend: ResultBackend | None = None


def get_backend() -> ResultBackend:
    global backend
    return backend


def set_backend(input: ResultBackend) -> None:
    global backend
    backend = input
    get_broker().add_middleware(Results(backend=input))
