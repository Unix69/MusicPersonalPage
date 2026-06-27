#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# Setup script (English + colored output)
# - Ensures Python >= 3.10 is available
# - Creates a virtual environment using the chosen interpreter
# - Upgrades pip and installs requirements
# ----------------------------

# ANSI color codes
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BLUE="\033[1;34m"
RESET="\033[0m"

# helper print functions
info()    { echo -e "${YELLOW}[INFO]${RESET} $*"; }
action()  { echo -e "${BLUE}[ACTION]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
failure() { echo -e "${RED}[ERROR]${RESET} $*"; }

# --- Desired minimum Python version ---
REQ_MAJOR=3
REQ_MINOR=10
CANDIDATES=("3.11" "3.10")

info "Checking installed python3 version..."

PY_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYM=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYN=$(python3 -c 'import sys; print(sys.version_info[1])')
    info "Found python3 ${PYM}.${PYN}"
    if [ "${PYM}" -eq "${REQ_MAJOR}" ] && [ "${PYN}" -ge "${REQ_MINOR}" ]; then
        PY_BIN="python3"
        success "Python version satisfies requirement (>= ${REQ_MAJOR}.${REQ_MINOR})."
    else
        info "Installed python3 is older than required (>= ${REQ_MAJOR}.${REQ_MINOR})."
    fi
fi

if [ -z "${PY_BIN}" ]; then
    failure "No compatible Python found. Please install Python >= ${REQ_MAJOR}.${REQ_MINOR}."
    exit 1
fi

info "Using interpreter: ${PY_BIN}"

# --- Remove previous venv if present ---
if [ -d "venv" ]; then
    action "Removing existing virtual environment 'venv'..."
    rm -rf venv
fi

# --- Create virtual environment ---
action "Creating virtual environment..."
"${PY_BIN}" -m venv venv
success "Virtual environment created."

# --- Activate virtual environment ---
source venv/bin/activate
success "Activated virtual environment."

# --- Upgrade pip / setuptools / wheel ---
action "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel
success "pip, setuptools, wheel upgraded."

# --- Create requirements.txt if missing ---
if [ ! -f requirements.txt ]; then
    action "Creating default requirements.txt..."
    cat > requirements.txt <<'REQ'
Flask==2.3.3
Flask-Admin==1.6.1
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.1.1
Werkzeug==2.3.7
WTForms==3.0.1
python-dotenv==1.0.0
Pillow==11.3.0   # <-- Aggiornata
email_validator==2.1.0.post1
REQ
    success "requirements.txt created."
fi

# --- Install requirements ---
action "Installing Python packages from requirements.txt..."
pip install -r requirements.txt
success "Python packages installed."

# --- Ensure static/images exists ---
action "Ensuring static/images directory exists..."
mkdir -p static/images
success "static/images ready."

success "Setup completed successfully!"
echo -e "${YELLOW}To start using the virtual environment:${RESET}"
echo -e "  ${BLUE}source venv/bin/activate${RESET}"
echo -e "${YELLOW}Then run your app (for example):${RESET}"
echo -e "  ${BLUE}python main.py${RESET}"
