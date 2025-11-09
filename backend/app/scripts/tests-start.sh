#! /usr/bin/env bash
set -e
set -x

hatch run python /app/app/tests_pre_start.py

bash ./scripts/test.sh "$@"
