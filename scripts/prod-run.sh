#!/bin/bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/../"

dcCommand="docker compose -f docker-compose.yml"
$dcCommand build
$dcCommand up -d
