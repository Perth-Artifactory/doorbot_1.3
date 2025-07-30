#!/bin/bash
set -e

VENV_DIR=".venv"

echo "🔧 Creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "⬆️  Upgrading pip and installing pip-tools..."
pip install --upgrade pip
pip install pip-tools

echo "📝 Compiling requirements..."
pip-compile --strip-extras requirements.in
pip-compile --strip-extras dev-requirements.in

echo "🔄 Syncing environment to dev-requirements.txt..."
pip-sync dev-requirements.txt

echo "✅ Done. Virtual environment ready. Use:"
echo "    source $VENV_DIR/bin/activate"
