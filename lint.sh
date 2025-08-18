#!/bin/bash

# Run Black for code formatting
echo "Running Black..."
poetry run black src/
poetry run black dashboard/

# Run Pylint
echo "Running Pylint..."
poetry run pylint src/
poetry run pylint dashboard/

# Run Mypy for type checking
echo "Running Mypy..."
poetry run mypy src/
poetry run mypy dashboardthat/

echo "Linting and type checking completed successfully!"
