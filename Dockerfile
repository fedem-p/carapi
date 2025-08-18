# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the Poetry lock file and configuration file
COPY pyproject.toml poetry.lock* README.md /app/

# Install dependencies, including dev dependencies for testing and linting
RUN poetry install

# Copy the entire application code and the linting script
COPY . /app/

# Make the linting script executable
RUN chmod +x /app/lint.sh /app/test.sh /app/update_make_models.sh

# Expose the Flask port for the dashboard
EXPOSE 5000

# Default command: run Flask dashboard (can be overridden for CLI)
CMD ["poetry", "run", "python", "dashboard/app.py"]
