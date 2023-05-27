# Worker Heartbeat Example
This is an example repo to show off some of the best practices and baseline functionality of our additions.


## Setup
1. Install docker and docker-compose ( https://docs.docker.com/compose/install/ )
2. Start docker ( https://docs.docker.com/config/daemon/start/ )
3. Install python > 3.10 ( https://www.python.org/downloads/ )
4. Install poetry ( https://python-poetry.org/docs/ )
5. Install the package: `poetry install`

## Run
### Worker and Scheduler
1. To start the docker services run: `docker-compose --env-file .env up --build -d`
   1. You should now see 4 services running: `redis`, `rabbitmq`, `dramatiq-worker` and `dramatiq-scheduler`
2. To verify the worker is running check the docker container
    ```
    $ docker logs dramatiq-worker --tail 2
    [2023-05-26 22:58:40,660] [PID 7] [Thread-11] [root] [INFO] Worker Heartbeat @ 1685141920.6606145
    [2023-05-26 22:58:45,656] [PID 7] [Thread-11] [root] [INFO] Worker Heartbeat @ 1685141925.6568296
    ```
## CLI
`cli.py` contains several commands for manually sending tasks.

```
$ python cli.py --help
Usage: cli.py [OPTIONS]

  Test Async Dramatiq Functionality

Options:
  --send_heartbeat   Send a heartbeat
  --sleep_for FLOAT  Sleep for N seconds
  --help             Show this message and exit.
```