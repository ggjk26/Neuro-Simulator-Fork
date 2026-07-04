#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
if [ -d "$REPO_ROOT/server" ]; then
  PYTHONPATH="$REPO_ROOT/server${PYTHONPATH:+:$PYTHONPATH}"
  export PYTHONPATH
fi
python -m neuro_simulator.launcher "$@"
