#!/bin/bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/../"

export MY_UID="$(id -u)"
export MY_GID="$(id -g)" 
docker compose run --rm migrations "$@"
