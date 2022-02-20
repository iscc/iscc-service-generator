#!/usr/bin/env bash
set -euo pipefail

if [ "${AUTO_MIGRATE-false}" == "true" ]; then
    poetry run python manage.py migrate --force-color
fi

exec "$@"
