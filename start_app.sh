#!/usr/bin/env bash
set -euo pipefail

# run_app.sh
# Launch helper for your Flask app.
# Usage:
#   ./run_app.sh [--daemon] [--log path/to/logfile] [--help]
# If venv exists it will be used automatically.

# ANSI color codes
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BLUE="\033[1;34m"
RESET="\033[0m"

info(){ echo -e "${YELLOW}[INFO]${RESET} $*"; }
action(){ echo -e "${BLUE}[ACTION]${RESET} $*"; }
ok(){ echo -e "${GREEN}[OK]${RESET} $*"; }
err(){ echo -e "${RED}[ERROR]${RESET} $*"; }

# Defaults
DAEMON=false
LOGFILE=""
ENTRY="main.py"

show_help(){
  cat <<EOF
Usage: $0 [options]

Options:
  --daemon           Run app in background (nohup). Writes PID to ./app.pid
  --log <file>       Path to logfile (defaults to ./app.log when --daemon)
  --python <path>    Force a specific python interpreter
  --entry <file>     Python entrypoint (default: ${ENTRY})
  --help             Show this help
EOF
}

# parse args (very simple)
while [[ $# -gt 0 ]]; do
  case "$1" in
    --daemon) DAEMON=true; shift ;;
    --log) LOGFILE="$2"; shift 2 ;;
    --python) FORCE_PY="$2"; shift 2 ;;
    --entry) ENTRY="$2"; shift 2 ;;
    --help) show_help; exit 0 ;;
    *) err "Unknown arg: $1"; show_help; exit 2 ;;
  esac
done

# find interpreter: prefer venv
PY=""
if [ -n "${FORCE_PY:-}" ]; then
  PY="$FORCE_PY"
  info "Using forced python interpreter: ${PY}"
fi

if [ -z "${PY:-}" ]; then
  if [ -x "./venv/bin/python" ]; then
    action "Activating virtualenv ./venv..."
    # shellcheck disable=SC1091
    source ./venv/bin/activate
    PY="./venv/bin/python"
    ok "Using ./venv/bin/python"
  else
    action "No venv found; checking system python3..."
    if command -v python3 >/dev/null 2>&1; then
      PY_SYS="python3"
      # check version >= 3.10
      PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])' 2>/dev/null || echo 0)
      PY_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])' 2>/dev/null || echo 0)
      if [ "${PY_MAJOR}" -lt 3 ] || ( [ "${PY_MAJOR}" -eq 3 ] && [ "${PY_MINOR}" -lt 10 ] ); then
        err "System python3 version is ${PY_MAJOR}.${PY_MINOR} - needs >= 3.10."
        err "Create a venv with a newer python or install Python >=3.10."
        exit 1
      fi
      PY="${PY_SYS}"
      ok "Using system python: ${PY} (version ${PY_MAJOR}.${PY_MINOR})"
    else
      err "No python3 found on PATH and no venv present. Run the setup script first."
      exit 1
    fi
  fi
fi

# entry exists?
if [ ! -f "${ENTRY}" ]; then
  err "Entrypoint ${ENTRY} not found in current directory ($(pwd))."
  exit 1
fi

# set default logfile if daemon and no logfile provided
if [ "${DAEMON}" = true ] && [ -z "${LOGFILE}" ]; then
  LOGFILE="./app.log"
fi

# run
if [ "${DAEMON}" = true ]; then
  action "Starting app in background (daemon mode)..."
  action "Logfile: ${LOGFILE}"
  nohup "${PY}" "${ENTRY}" > "${LOGFILE}" 2>&1 &
  PID=$!
  echo "${PID}" > ./app.pid
  ok "App started (PID ${PID}). PID file: ./app.pid"
  ok "Tail log with: tail -f ${LOGFILE}"
  exit 0
else
  action "Starting app in foreground with interpreter: ${PY}"
  ok "Press Ctrl+C to stop."
  exec "${PY}" "${ENTRY}"
fi
