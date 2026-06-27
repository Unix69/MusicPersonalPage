#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# Setup script (English + colored output)
# Ensures Python >= 3.10 is available
# ----------------------------

# ANSI color codes
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BLUE="\033[1;34m"
RESET="\033[0m"

info()    { echo -e "${YELLOW}[INFO]${RESET} $*"; }
action()  { echo -e "${BLUE}[ACTION]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
failure() { echo -e "${RED}[ERROR]${RESET} $*"; }

REQ_MAJOR=3
REQ_MINOR=10

# --- Move to the script directory ---
cd "$(dirname "$0")"

# --- find candidate interpreter ---
PY_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYM=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYN=$(python3 -c 'import sys; print(sys.version_info[1])')
    info "Found python3 ${PYM}.${PYN}"
    if [ "${PYM}" -eq "${REQ_MAJOR}" ] && [ "${PYN}" -ge "${REQ_MINOR}" ]; then
        PY_BIN="python3"
    fi
fi

if [ -z "${PY_BIN}" ] && command -v python >/dev/null 2>&1; then
    PYM=$(python -c 'import sys; print(sys.version_info[0])')
    PYN=$(python -c 'import sys; print(sys.version_info[1])')
    info "Found python ${PYM}.${PYN}"
    if [ "${PYM}" -eq "${REQ_MAJOR}" ] && [ "${PYN}" -ge "${REQ_MINOR}" ]; then
        PY_BIN="python"
    fi
fi

if [ -z "${PY_BIN}" ]; then
    failure "No compatible Python (>=${REQ_MAJOR}.${REQ_MINOR}) found."
    read -p "Do you want to install Python ${REQ_MAJOR}.${REQ_MINOR}+ now? [y/N]: " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        action "Installing Python ${REQ_MAJOR}.${REQ_MINOR}+ ..."
        sudo apt update
        sudo apt install -y python3.12 python3.12-venv python3.12-distutils || true
        PY_BIN="python3.12"
        sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
        success "Python ${REQ_MAJOR}.${REQ_MINOR}+ installed and set."
    else
        failure "You must install Python >=${REQ_MAJOR}.${REQ_MINOR} with ensurepip support."
        exit 1
    fi
fi

info "Using interpreter: ${PY_BIN}"

# --- check pip availability ---
if ! "${PY_BIN}" -m pip --version >/dev/null 2>&1; then
    failure "pip is not available in ${PY_BIN}."
    read -p "Do you want to bootstrap pip manually (get-pip.py)? [y/N]: " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        action "Bootstrapping pip..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | "${PY_BIN}"
        success "pip installed."
    else
        failure "pip is required. Exiting."
        exit 1
    fi
fi

# --- Remove previous venv if present ---
if [ -d "venv" ]; then
    action "Removing existing virtual environment 'venv'..."
    rm -rf venv
fi

# --- Create virtual environment ---
action "Creating virtual environment..."
if ! "${PY_BIN}" -m venv venv; then
    info "Falling back: creating venv without pip (no ensurepip support)..."
    "${PY_BIN}" -m venv venv --without-pip
    action "Bootstrapping pip into venv..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | ./venv/bin/python
fi
success "Virtual environment created."

# --- Activate virtual environment ---
# shellcheck source=/dev/null
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
email_validator==2.1.0.post1
REQ
    success "requirements.txt created."
fi

# --- Install requirements ---
action "Installing Python packages from requirements.txt..."
pip install -r requirements.txt
success "Python packages installed."

# --- Ensure static directories ---
for dir in static/images static/images/profile static/images/album static/icons static/css; do
    action "Ensuring ${dir} exists..."
    mkdir -p "$dir"
    success "${dir} ready."
done

# --- Move SVG icons ---
action "Moving SVG icons to static/icons..."
shopt -s nullglob
for svg in ./*.svg; do
    if [ -f "$svg" ]; then
        mv -v "$svg" static/icons/
    fi
done
shopt -u nullglob
success "SVG icons moved to static/icons."

# --- Move cover image ---
if [ -f "cover.jpg" ]; then
    action "Moving cover.jpg to static/images/profile/..."
    mv -v "cover.jpg" static/images/profile/
    success "cover.jpg moved."
else
    info "cover.jpg not found, skipping."
fi

# --- Move style.css ---
if [ -f "style.css" ]; then
    action "Moving style.css to static/css/..."
    mv -v "style.css" static/css/
    success "style.css moved."
else
    info "style.css not found, skipping."
fi

success "Setup completed successfully!"
echo -e "${YELLOW}To start using the virtual environment:${RESET}"
echo -e "  ${BLUE}source venv/bin/activate${RESET}"
echo -e "${YELLOW}Then run your app (for example):${RESET}"
echo -e "  ${BLUE}python main.py${RESET}"
