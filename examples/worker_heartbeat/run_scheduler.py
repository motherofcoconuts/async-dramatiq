# Standard Library Imports
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from worker_heartbeat import tasks  # noqa : F401

# Local Application Imports
from async_dramatiq import scheduler as tasks_scheduler


def main() -> None:
    """Run the apscheduler in a seperate process."""

    scheduler = BlockingScheduler()
    for job in tasks_scheduler.scheduled_jobs:
        job_path = f"{job.module_path}:{job.func_name}.send"
        job_name = f"{job.module_path}.{job.func_name}"
        scheduler.add_job(job_path, trigger=job.trigger, name=job_name)

    def shutdown(signum, frame):
        scheduler.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    scheduler.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
