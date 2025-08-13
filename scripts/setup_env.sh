#!/bin/bash

# === CONFIG ===
ENV_NAME="website_scrapers_env"
PYTHON_VERSION="python3"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# === CREATE ENVIRONMENT ===
echo "Creating virtual environment: $ENV_NAME"
$PYTHON_VERSION -m venv "$PROJECT_ROOT/$ENV_NAME"

# === ACTIVATE ENVIRONMENT ===
echo "Activating environment..."
source "$PROJECT_ROOT/$ENV_NAME/bin/activate"

# === INSTALL BASIC DEPENDENCIES ===
echo "Installing common scraping packages..."
pip install --upgrade pip
pip install playwright beautifulsoup4 requests pip-tools

# Optional: download Playwright drivers
playwright install

# === INSTALL PROJECT DEPENDENCIES ===
echo "Installing project dependencies..."
if [ -f "$BACKEND_DIR/requirements.in" ]; then
    echo "Found requirements.in, installing dependencies..."
    cd "$BACKEND_DIR"
    pip install -r requirements.in
    pip install -e .
    cd "$PROJECT_ROOT"
else
    echo "No requirements.in found, creating basic requirements.txt..."
    pip freeze > "$PROJECT_ROOT/requirements.txt"
fi

# === CREATE .GITIGNORE IF MISSING ===
if [ ! -f "$PROJECT_ROOT/.gitignore" ]; then
  echo "Creating .gitignore file..."
  touch "$PROJECT_ROOT/.gitignore"
fi

# === APPEND STANDARD PYTHON IGNORE RULES ===
echo "Adding venv and large file rules to .gitignore..."
cd "$PROJECT_ROOT"
grep -qxF "$ENV_NAME/" .gitignore || echo "$ENV_NAME/" >> .gitignore
grep -qxF '__pycache__/' .gitignore || echo '__pycache__/' >> .gitignore
grep -qxF '*.pyc' .gitignore || echo '*.pyc' >> .gitignore
grep -qxF '*.DS_Store' .gitignore || echo '*.DS_Store' >> .gitignore
grep -qxF '*.log' .gitignore || echo '*.log' >> .gitignore
grep -qxF '*.sqlite3' .gitignore || echo '*.sqlite3' >> .gitignore
grep -qxF '*.db' .gitignore || echo '*.db' >> .gitignore

# === FINISH ===
echo "✅ Setup complete. You are now in the '$ENV_NAME' environment."
echo "To activate it later, run: source $PROJECT_ROOT/$ENV_NAME/bin/activate"
echo "Project root: $PROJECT_ROOT"
