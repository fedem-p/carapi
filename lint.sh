#!/bin/bash

# Run Black for code formatting
echo "Running Black..."
poetry run black src/

# Run Pylint
echo "Running Pylint..."
poetry run pylint src/

# Run Mypy for type checking
echo "Running Mypy..."
poetry run mypy src/

echo "Linting and type checking completed successfully!"
