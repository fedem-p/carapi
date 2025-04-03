#!/bin/bash

# Run Tests with Coverage
echo "Running Tests with Coverage..."
poetry run python -m pytest --cov=src tests/

echo "Tests completed successfully!"
