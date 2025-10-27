#!/bin/bash

# Setup script for JobBider

echo "================================================"
echo "  JobBider - Automated Job Application Setup"
echo "================================================"

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p resumes

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your credentials."
else
    echo ""
    echo ".env file already exists."
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from src.database import Database; db = Database(); print('✓ Database initialized')"

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Dice credentials"
echo "2. Edit config.yaml with your job preferences"
echo "3. Place your resume in resumes/resume.pdf"
echo "4. Run: python main.py --help"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
