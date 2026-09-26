#!/bin/bash
set -e

# Create and activate virtual environment in /tmp outside project folder
# This ensures pygbag does not scan or package the virtual environment
VENV_DIR="${TMPDIR:-/tmp}/arcade_venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Install dependencies into virtual environment
pip install -r requirements.txt

# Build the project (creates build/web directory, --no_opt avoids ffmpeg/asset optimizer crashes)
python -m pygbag --build --no_opt --disable-sound-format-error .

# Inject Vercel Analytics into the built index.html
python inject_analytics.py
