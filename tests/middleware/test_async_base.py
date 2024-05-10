# Standard Library Imports
from typing import Any
from unittest import mock

import dramatiq as dq
import pytest

# Local Application Imports
from async_dramatiq.middleware.async_base import AsyncMiddleware


def test_async_base(broker: dq.Broker, worker: dq.Worker) -> None:
    import async_dramatiq.middleware.async_base as async_base

    async_base.is_initialized = False

    with mock.patch(
        "async_dramatiq.worker.AsyncWorker.start"
    ) as mock_async_worker_start, mock.patch("threading.Event.wait", return_value=True):
        async_middlware = AsyncMiddleware()
        async_middlware.before_worker_boot(broker, worker)

    mock_async_worker_start.assert_called()


def test_async_base_only_callable_once(broker: dq.Broker, worker: dq.Worker) -> None:
    import async_dramatiq.middleware.async_base as async_base

    async_base.is_initialized = False

    with mock.patch(
        "async_dramatiq.worker.AsyncWorker.start"
    ) as mock_async_worker_start, mock.patch("threading.Event.wait", return_value=True):
        with pytest.raises(RuntimeError):
            async_middlware = AsyncMiddleware()
            async_middlware.before_worker_boot(broker, worker)
            async_middlware.before_worker_boot(broker, worker)

    mock_async_worker_start.assert_called_once()
