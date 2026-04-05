#!/bin/bash
# Launcher script for PDF Searcher

cd "$(dirname "$0")"

# Run the application (uses built-in tkinter)
python3 pdf_searcher.py "$@"