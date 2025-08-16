#!/bin/bash

echo "Running tests with coverage..."
docker exec fastapi_server bash -c "cd /app && python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v"

echo ""
echo "Coverage report generated in htmlcov/index.html"
echo "Open htmlcov/index.html in your browser to view detailed coverage report" 
echo "If inside docker and server/htmlcov is not accessible, run: cd server/htmlcov && python3 -m http.server 8473"