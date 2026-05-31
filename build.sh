#!/bin/bash
# Install dependencies
pip install -r requirements.txt
pip install pygbag

# Build the project (creates build/web directory)
pygbag --build --disable-sound-format-error .

# Inject Vercel Analytics into the built index.html
python inject_analytics.py
