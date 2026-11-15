#!/usr/bin/env bash
# Usage: ./run.sh demo | ./run.sh test | ./run.sh <any privacy_toolkit command>
cd "$(dirname "$0")"
case "$1" in
  test) PYTHONPATH=src python3 -m pytest -q ;;
  *)    PYTHONPATH=src python3 -m privacy_toolkit --root . "$@" ;;
esac
