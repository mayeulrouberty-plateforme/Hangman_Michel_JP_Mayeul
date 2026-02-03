#!/bin/bash
echo "=== Cosmic Query Agent ==="
echo

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if dependencies installed
if ! pip show streamlit > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo
echo "Starting application..."
echo "Open http://localhost:8501 in your browser"
echo

streamlit run app.py
