#!/bin/bash

# Run Black for code formatting
echo "Running Black..."
poetry run black src/
poetry run black dashboard/
poetry run black tests/

# Run Pylint
echo "Running Pylint..."
PYTHONPATH=$(pwd) poetry run pylint src/
poetry run pylint dashboard/

# Run Mypy for type checking
echo "Running Mypy..."
poetry run mypy --explicit-package-bases src/
poetry run mypy --explicit-package-bases dashboard/

echo "Linting and type checking completed successfully!"
