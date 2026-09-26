#!/bin/bash
set -e

# Create and activate virtual environment (bypasses PEP 668 externally-managed-environment)
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install dependencies into virtual environment
pip install -r requirements.txt

# Build the project (creates build/web directory)
python -m pygbag --build --disable-sound-format-error .

# Inject Vercel Analytics into the built index.html
python inject_analytics.py
