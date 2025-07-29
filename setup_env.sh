#!/bin/bash

# === CONFIG ===
ENV_NAME="website_scrapers_env"
PYTHON_VERSION="python3"  # change if using pyenv or custom install

# === CREATE ENVIRONMENT ===
echo "Creating virtual environment: $ENV_NAME"
$PYTHON_VERSION -m venv ~/$ENV_NAME

# === ACTIVATE ENVIRONMENT ===
echo "Activating environment..."
source ~/$ENV_NAME/bin/activate

# === INSTALL BASIC DEPENDENCIES ===
echo "Installing common scraping packages..."
pip install --upgrade pip
pip install playwright beautifulsoup4 requests

# Optional: download Playwright drivers
playwright install

# === CREATE REQUIREMENTS.TXT ===
echo "Freezing environment to requirements.txt..."
pip freeze > requirements.txt

# === CREATE .GITIGNORE IF MISSING ===
if [ ! -f .gitignore ]; then
  echo "Creating .gitignore file..."
  touch .gitignore
fi

# === APPEND STANDARD PYTHON IGNORE RULES ===
echo "Adding venv and large file rules to .gitignore..."
grep -qxF 'venv/' .gitignore || echo 'venv/' >> .gitignore
grep -qxF '__pycache__/' .gitignore || echo '__pycache__/' >> .gitignore
grep -qxF '*.pyc' .gitignore || echo '*.pyc' >> .gitignore
grep -qxF '*.DS_Store' .gitignore || echo '*.DS_Store' >> .gitignore
grep -qxF '*.log' .gitignore || echo '*.log' >> .gitignore
grep -qxF '*.sqlite3' .gitignore || echo '*.sqlite3' >> .gitignore
grep -qxF '*.db' .gitignore || echo '*.db' >> .gitignore
grep -qxF '*.json' .gitignore || echo '# *.json (comment out if needed)' >> .gitignore

# === FINISH ===
echo "✅ Setup complete. You are now in the '$ENV_NAME' environment."
echo "To activate it later, run: source ~/$ENV_NAME/bin/activate"
