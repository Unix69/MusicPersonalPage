# 🚀 Getting Started & Deployment Guide

Follow these sequential setup operations to configure, deploy, and launch the platform across development or enterprise-grade production runtime instances.

---

## 🎛️ System Prerequisites
Before initializing the installer routines, verify that your target platform contains the following packages:
* **Python Interpreter**: Version <code>3.9</code>, <code>3.10</code>, or <code>3.11</code>.
* **Compiler Base**: Standard C development tooling if building extensions for production SQLite or PostgreSQL drivers.

---

## 📦 Environment Setup & Dependencies Installation

Execute the following commands inside your shell terminal workspace to initialize a virtualized, isolated system space and install required packages:

<pre><code>
# 1. Clone or step into your target repository folder
cd music-web-engine

# 2. Allocate an isolated virtual environment
python -m venv venv

# 3. Trigger activation depending on your operating system shell
# For Linux/macOS environments:
source venv/bin/activate
# For Windows PowerShell environments:
# .\venv\Scripts\Activate.ps1

# 4. Perform dependency tree deployment
pip install --upgrade pip
pip install -r requirements.txt
</code></pre>

---

## ⚙️ Configuration Variables Blueprint

The system architecture rejects hardcoded production variables. You must populate an infrastructure file named exactly <code>music_web_page.env</code> located directly within the project root folder.

Create the file and configure it as follows:

<pre><code>
# System Security Token
SECRET_KEY=generate_a_high_entropy_alphanumeric_string_here

# Relational Database Storage Directive
DATABASE_URI=sqlite:///music.db

# Administrative Credentials Barrier Config
ADMIN_USERNAME=musician_admin
ADMIN_PASSWORD=protect_your_production_workspace_with_a_strong_password

# Interface Configuration Mode
ADMIN_APP_TEMPLATE_MODE=bootstrap4
ADMIN_APP_NAME=Artist Backoffice Workspace

# WSGI Deployment Operational Toggle
# Set to 'True' when mounting inside an enterprise Gunicorn / uWSGI runner wrapper
APP_WSGI_MODE_ENABLE=False
</code></pre>

---

## ⚡ Application Execution Ramps

### 🧑‍💻 Local Engineering Development Run
To trigger instant execution using the active debugger server thread pool, launch the included wrapper script:

<pre><code>bash start_app.sh</code></pre>

Alternatively, run the main Python module file directly:

<pre><code>python main.py</code></pre>

### 🏭 Enterprise Production Mount Process
When deploying to public cloud servers, toggle the environment configuration flag <code>APP_WSGI_MODE_ENABLE=True</code> within your <code>music_web_page.env</code> file. This bypasses the development server and safely exposes the application instance to upstream WSGI servers such as Gunicorn:

<pre><code>gunicorn -w 4 -b 0.0.0.0:8000 "main:application"</code></pre>