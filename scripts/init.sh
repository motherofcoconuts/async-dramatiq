# /bin/bash

poetry install
source .venv/bin/activate
pre-commit install
pre-commit autoupdate