# Tests

This directory contains the test suite for the czi2tif project.

## Structure

- `test_czi2tif.py` - Tests for the main czi2tif functionality and CLI
- `test_read.py` - Tests for the CZI and LIF file reading functionality
- `test_export.py` - Tests for the export parameters and functionality
- `test_integration.py` - Integration tests for the complete pipeline
- `test_logging.py` - Tests for the logging functionality
- `fixtures/` - Test data and fixtures
  - `sample_files/` - Sample CZI and LIF files for testing

## Test Coverage

The test suite covers:

### File Format Support

- CZI file reading and processing
- LIF file reading and processing
- Unsupported file format handling

### Resolution Extraction

- Metadata resolution extraction from CZI files
- LIF scale information handling
- Fallback behavior for missing resolution data

### Image Processing

- Scene-based processing
- Stack-based processing (Z-dimensions)
- Mosaic detection and handling
- Multi-channel support

### CLI Interface

- Command-line argument parsing
- File and directory processing
- Recursive directory traversal
- Output directory configuration
- Logging configuration (verbose, quiet, file output)
- Bit depth selection

### Export Functionality

- TIFF file generation with proper metadata
- Resolution information preservation
- Directory creation

### Error Handling

- File reading errors
- Processing errors
- Unsupported format errors

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

## Test Guidelines

- Follow the `test_*.py` naming convention
- Use descriptive test function names that start with `test_`
- Group related tests in classes
- Use mocking for external dependencies
- Test both success and failure cases
- Include integration tests for complete workflows

## Adding Tests

When adding new functionality, please add corresponding tests. Test files should:

- Follow the `test_*.py` naming convention
- Mirror the structure of the source code
- Include docstrings describing what is being tested
- Use descriptive test function names that start with `test_`

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
