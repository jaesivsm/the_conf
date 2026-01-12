# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`the_conf` is a Python configuration management library that merges configuration from multiple sources (files, command line, environment variables) with configurable priority ordering. It uses a "meta configuration" file (YAML/JSON) to define parameter schemas, and then loads actual values from various sources.

## Development Commands

### Testing
```bash
# Run all tests
make test
# or
poetry run pytest

# Run specific test file
poetry run pytest tests/test_the_conf.py

# Run specific test
poetry run pytest tests/test_the_conf.py::TestTheConfObj::test_conf_loading
```

### Linting
```bash
# Run all linters (mypy, pycodestyle, black)
make lint

# Run individual linters
poetry run mypy the_conf
poetry run pycodestyle the_conf
poetry run black --check the_conf
```

## Code Style Requirements

This project enforces strict code style with automated linting:

### Line Length
- **Maximum 79 characters per line** (pycodestyle E501)
- Configured in `pyproject.toml` with `line-length = 79` for black
- This includes comments - keep them concise
- Example violation: `# Skip list options (paths containing Index) as they're not supported on cmd line` (89 chars)
- Fixed version: `# List options (paths with Index) not supported on cmd line` (67 chars)

### Formatting
- **Black formatter** with Python 3.9+ target
- Run `poetry run black the_conf` to auto-format
- All code must pass `black --check` before committing

### Type Checking
- **mypy** for static type checking
- All code must be type-safe
- Use type hints for function parameters and return values

### Style Checking
- **pycodestyle** (formerly pep8) for PEP 8 compliance
- Checks indentation, whitespace, naming conventions
- Must pass with zero violations

**Before committing:** Always run `make lint` to ensure all checks pass.

### Build & Deploy
```bash
# Build distribution (runs lint and test first)
make build

# Install dependencies
make install  # or poetry update
```

## Architecture

### Core Concepts

**Two-Phase Configuration System:**
1. **Meta Configuration** (the_conf.example.yml): Defines the schema - parameter names, types, defaults, validators, choices
2. **User Configuration**: Actual values loaded from files/cmd/env that conform to the meta configuration schema

**Source Priority System:**
- Configured via `source_order` in meta configuration (default: `["cmd", "files", "env"]`)
- **First-wins priority**: The first source in `source_order` to provide a value wins
- Later sources do NOT overwrite values from earlier sources
- Critical: All load methods (`_load_files`, `_load_cmd`, `_load_env`) use `overwrite=False` to implement this behavior

### Key Components

**the_conf/the_conf.py - TheConf class:**
- Main entry point, inherits from `ConfNode`
- `load()`: Iterates through `source_order` and calls corresponding load methods
- `_load_files()`, `_load_cmd()`, `_load_env()`: Load from each source
- Uses `_set_to_path(path, value, overwrite=False)` to respect priority

**the_conf/node.py - Node hierarchy:**
- `AbstractNode`: Base class with parameter loading logic
- `ConfNode`: Represents dict-like configuration nodes (nested objects)
- `ListNode`: Represents list parameters, inherits from both `list` and `AbstractNode`
- Uses `_get_path_val_param()` to iterate all paths/values/parameters
- The `Index` class (from utils.py) is used as a placeholder in paths for list indices

**the_conf/command_line.py:**
- Generates argparse parsers from parameter definitions
- **Important**: List options (paths containing `Index`) are automatically skipped because argparse cannot handle dynamic list indices
- `path_to_cmd_opt()`: Converts paths to command line flags (e.g., `['nested', 'value']` → `--nested-value`)

**the_conf/environement.py:**
- Handles environment variable parsing with support for nested paths and lists
- `iter_on_environ_from_path()`: Matches environ keys against path patterns, including regex matching for list indices
- Handles malformed ENV (non-consecutive indices) by compacting them

**the_conf/files.py:**
- YAML/JSON file reading with optional encryption (pycryptodome)
- `extract_values()`: Extracts configuration values matching parameter paths

### Special Parameter Types

**List Options:**
- Defined with `{"type": "list", "name": [child_params]}`
- Simple lists: `{"type": "list", "intlist": {"type": int}}`
- Complex lists: `{"type": "list", "dictlist": [{"field1": {...}}, {"field2": {...}}]}`
- **Command line limitation**: List options are automatically skipped during CLI parsing (paths with `Index` are filtered out)
- ENV syntax: `LISTNAME_0`, `LISTNAME_1`, `DICTLIST_0_FIELD`, etc.
- File syntax: Standard YAML/JSON arrays

**Parameter Options:**
- `type`: Python type or string mapping (int, str, bool, list, dict)
- `default`: Default value (cannot be used with `required`)
- `required`: Must be provided from at least one source
- `among`: List of valid choices
- `read_only`: Prevents modification after initial load
- `no_cmd`: Skip this parameter for command line parsing
- `no_env`: Skip this parameter for environment variable parsing
- `cmd_line_opt`: Override auto-generated CLI flag name

## Testing Patterns

When testing configuration loading:
- Use `mock.patch("the_conf.files.read")` to mock file reading
- Pass `cmd_line_opts=[]` list and `environ={}` dict to TheConf constructor
- Test source priority by providing same value from multiple sources
- List option tests use both integer ENV values and string values (ENV autocasts via parameter type)

## Important Implementation Details

### Source Priority Bug History
- Originally (commit 81aa069e, 2023): All load methods used `overwrite=True` for list support
- Partial fix (commit 2a200e8, 2024-12): `_load_env()` changed to `overwrite=False`
- Complete fix (commit fc1030c, 2025): `_load_files()` and `_load_cmd()` changed to `overwrite=False`
- **Key principle**: First source in `source_order` has priority and should never be overwritten

### List Index Handling
- `Index` class is used as a type marker in paths: `['mylist', Index, 'field']`
- Command line parser explicitly skips paths containing `Index` (they cause TypeError in `str.lower()`)
- ENV and FILES sources properly handle list indices via different mechanisms
