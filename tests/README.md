# Tests

This directory contains the test suite for the czi2tif project.

## Structure

- `test_czi2tif.py` - Tests for the main czi2tif functionality
- `test_read.py` - Tests for the CZI file reading functionality
- `test_logging.py` - Tests for the logging functionality
- `fixtures/` - Test data and fixtures
  - `sample_files/` - Sample CZI files for testing

## Running Tests

To run all tests:
```bash
uv run pytest
```

To run tests with coverage:
```bash
uv run pytest --cov=src/czi2tif
```

To run a specific test file:
```bash
uv run pytest tests/test_czi2tif.py
```

## Adding Tests

When adding new functionality, please add corresponding tests. Test files should:
- Follow the `test_*.py` naming convention
- Mirror the structure of the source code
- Include docstrings describing what is being tested
- Use descriptive test function names that start with `test_` 