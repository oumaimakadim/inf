#!/bin/bash

echo "=========================================="
echo "AI Video Generator - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.8-3.10
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ] && [ "$minor" -le 10 ]; then
    echo "✓ Python version is compatible"
else
    echo "⚠ Warning: Python 3.8-3.10 recommended for best compatibility"
    echo "  Current version: $python_version"
fi

echo ""

# Install system dependencies
echo "Installing system dependencies..."

if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu system"
    sudo apt-get update
    sudo apt-get install -y ffmpeg git
elif command -v brew &> /dev/null; then
    echo "Detected macOS system"
    brew install ffmpeg git
else
    echo "⚠ Please install FFmpeg and Git manually"
fi

echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""

# Run model setup
echo "Setting up models and repositories..."
python utils/model_downloader.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run Streamlit app: streamlit run app.py"
echo ""
