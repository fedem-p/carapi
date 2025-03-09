#!/bin/bash

echo "Updating the current saved make and models"
poetry run python -m src.fetch_makes_and_models

echo "Update completed successfully!"
