#!/bin/bash

# Linux Spider Web Scanner - Run Script
# Quick script to run the scanner

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run install.sh first:"
    echo "  bash install.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the scanner
python3 main.py

# Deactivate on exit
deactivate
