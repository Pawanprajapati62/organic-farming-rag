#!/bin/sh
set -eu

data_dir="${RAG_DATA_DIR:-/data}"

if [ "$(id -u)" = "0" ]; then
    mkdir -p "$data_dir"
    chown -R app:app "$data_dir"
    exec gosu app "$@"
fi

exec "$@"
