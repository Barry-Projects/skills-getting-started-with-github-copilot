#!/bin/bash

# Test runner script for the FastAPI application

echo "Running FastAPI Application Tests"
echo "=================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "Test run completed!"
echo "Coverage report generated in htmlcov/index.html"