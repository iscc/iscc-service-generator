#!/usr/bin/env bash
set -euo pipefail

poetry install --ansi
poetry run python manage.py migrate --force-color

exec "$@"
