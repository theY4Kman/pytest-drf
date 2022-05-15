#!/bin/bash
poetry install -v --no-root \
 && poetry run pip install "$@"
