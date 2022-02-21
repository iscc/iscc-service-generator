#!/usr/bin/env bash
set -euo pipefail

until poetry run python -m dev.db_connection_check; do
    echo "Still waiting for database…"
    sleep 1
done

if [ "${AUTO_MIGRATE_AND_INSTALL-false}" == "true" ]; then
    poetry run python -c 'import dev.install; dev.install.migrate(); dev.install.create_demo_user(secure=False)'
fi

exec "$@"
