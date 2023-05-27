# Standard Library Imports
import sys
from dataclasses import dataclass

# Use IntEnum if Python version is greater than 3.11
if sys.version_info < (3, 11):
    from enum import Enum as IntEnum
else:
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
