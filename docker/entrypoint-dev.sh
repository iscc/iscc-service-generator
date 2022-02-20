#!/usr/bin/env bash
set -euo pipefail

if [ "${AUTO_MIGRATE-false}" == "true" ]; then
    poetry run python -c 'import dev.install; dev.install.migrate(); dev.install.create_demo_user(secure=False)'
fi

exec "$@"
