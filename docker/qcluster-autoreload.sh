#!/usr/bin/env bash
set -euo pipefail

PID_FILE=/tmp/qcluster.pid

function start_qcluster() {
    echo "--> Starting qcluster"
    poetry run python manage.py qcluster & echo $$! > $PID_FILE
}

function kill_qcluster() {
    echo "--> Killing qcluster"
    pid=$(cat $PID_FILE)
    rkill "$pid"
}

function restart_qcluster() {
    echo "--> Restarting qcluster"
    kill_qcluster
    start_qcluster
}

start_qcluster

while inotifywait --exclude "[^p].$|[^y]$" -e modify -r .; do
    restart_qcluster
done
