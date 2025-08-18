# Copilot Coding Agent Onboarding Instructions

## High-Level Repository Overview

This repository is a Python-based project for scraping, processing, and exporting car listing data from Autoscout24. It includes a modular scraper, configuration management, data normalization, and test coverage. The codebase is medium-sized, with a clear separation between source code (`src/`), tests (`tests/`), and data/configuration files. The main language is Python 3.11, and the project uses Poetry for dependency management and virtual environments. Linting is enforced with Pylint, and type checking is performed with Mypy. Test coverage is measured with pytest and pytest-cov.

## Build, Test, and Validation Instructions

### Environment Setup
- **Always** use Python 3.11.x (see Dockerfile for reference version).
- **Always** use Poetry for dependency management. Install Poetry if not present:
  ```bash
  pip install poetry
  ```
- Install dependencies:
  ```bash
  poetry install
  ```
- Activate the Poetry shell for all commands:
  ```bash
  poetry shell
  ```

### Linting and Type Checking
- Lint the codebase with Pylint:
  ```bash
  poetry run pylint src
  ```
- Type check with Mypy:
  ```bash
  poetry run mypy src
  ```
- Both should pass with no errors or warnings before submitting changes.

### Testing
- Run all tests and measure coverage:
  ```bash
  bash ./test.sh
  ```
  or
  ```bash
  poetry run pytest --cov=src
  ```
- Tests are located in `tests/`. Coverage reports are output to `htmlcov/`.
- **Always** ensure all tests pass before submitting changes.

### Running the Application
- The main entrypoint is `src/main.py`, which is executed as a module using:
  ```bash
  poetry run python -m src.main
  ```
- This is also the default command in `docker-compose.yml`:
  ```yaml
  command: ["poetry", "run", "python", "-m", "src.main"]
  ```
- See `README.md` for usage patterns or add new entrypoints as needed.

### Cleaning and Rebuilding
- If you encounter environment issues, remove the `.venv` directory and re-run `poetry install`.
- If Docker is used, rebuild containers with:
  ```bash
  docker-compose build
  docker-compose up
  ```

## Project Layout and Key Files

- `src/` — Main source code (scraper, config, constants, etc.)
- `tests/` — Unit and integration tests
- `data/` — Input data and CSVs for makes/models
- `Dockerfile`, `docker-compose.yml` — Containerization and orchestration
- `pyproject.toml`, `poetry.lock` — Poetry configuration and dependency lock
- `pytest.ini` — Pytest configuration
- `lint.sh`, `test.sh` — Helper scripts for linting and testing
- `README.md` — Project overview and usage
- `.github/` — GitHub workflows and Copilot instructions
- `htmlcov/` — Coverage reports (generated)

## Validation and CI
- **Always** run lint, type check, and all tests before submitting or merging code.
- Check for GitHub Actions workflows in `.github/workflows/` (if present) for additional CI steps.
- Ensure that any new dependencies are added to `pyproject.toml` and locked with `poetry lock`.
- If adding new scripts or entry points, document them in the `README.md`.

## Additional Guidance
- Trust these instructions for build, test, and validation steps. Only perform additional searches if information here is incomplete or in error.
- Avoid running shell commands outside of Poetry's environment unless explicitly required.
- If you encounter a build or test failure, check for missing dependencies, environment mismatches, or outdated lock files.
- Use the provided scripts (`lint.sh`, `test.sh`) for consistent validation.
- Prioritize making changes in `src/` for core logic and `tests/` for test coverage.
- Configuration and constants are in `src/config.py` and `src/constants.py`.
- For new features, add corresponding tests in `tests/` and update documentation as needed.

---

**Root directory files:**
- Dockerfile
- docker-compose.yml
- LICENSE
- lint.sh
- output.log
- poetry.lock
- pyproject.toml
- pytest.ini
- README.md
- test.sh
- update_make_models.sh

**Key subdirectories:**
- `src/`: Python modules for scraping and processing
- `tests/`: Test cases and HTML samples
- `data/`: CSVs and results
- `htmlcov/`: Coverage output

**README.md** provides further usage and setup details. Review it for the latest project-specific instructions.
