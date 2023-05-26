# Standard Library Imports
from dataclasses import dataclass
from enum import IntEnum


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
