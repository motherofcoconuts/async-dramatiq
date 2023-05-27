# Standard Library Imports
import logging
import os
from distutils.util import strtobool

import pika

# Environment Variables
testing: bool = strtobool(os.getenv("TESTING", "false"))
broker_host: str = os.getenv("BROKER_HOST", "localhost")
broker_port: int = os.getenv("BROKER_PORT", 5672)
broker_credentials: pika.PlainCredentials = pika.PlainCredentials(
    os.getenv("BROKER_USER", "guest"), os.getenv("BROKER_PASSWORD", "guest")
)
redis_host: str = os.getenv("REDIS_HOST", "localhost")
redis_port: int = os.getenv("REDIS_PORT", 6379)

# Setup
logging.basicConfig(level=logging.DEBUG if testing else logging.WARNING)
