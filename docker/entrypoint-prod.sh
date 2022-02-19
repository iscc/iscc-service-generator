#!/usr/bin/env bash
set -euo pipefail

if [ "${AUTO_MIGRATE-false}" == "true" ]; then
    python manage.py migrate
fi

exec "$@"
