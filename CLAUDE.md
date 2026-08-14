# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a command-line audio conversion tool that converts WAV files to OGG format using Python and uv for package management. The application supports both single file conversion and batch processing of directories.

## Architecture

The project follows a modular CLI architecture:
- **CLI Module (`wav_to_ogg/cli.py`)**: Command-line interface with argument parsing
- **Converter Module (`wav_to_ogg/converter.py`)**: Core audio conversion logic using pydub
- **Utils Module (`wav_to_ogg/utils.py`)**: Utility functions for logging, validation, and file operations
- **Package Init (`wav_to_ogg/__init__.py`)**: Package initialization and version info

## Key Components

- `wav_to_ogg/cli.py`: Command-line interface and main entry point
- `wav_to_ogg/converter.py`: AudioConverter class handling file/directory conversion
- `wav_to_ogg/utils.py`: Utility functions for logging, validation, and file operations
- `pyproject.toml`: Project metadata and dependencies (PEP 621, managed with uv)
- `uv.lock`: Dependency lock file
- `requirements.txt`: pip-compatible dependency list

## Development Commands

### Setup and Installation
```bash
# Install dependencies with uv (recommended)
uv sync

# Alternative: Install with pip
pip install -r requirements.txt
pip install -e .
```

### Running the Application
```bash
# Single file conversion
wav-to-ogg audio.wav

# Directory conversion
wav-to-ogg /path/to/audio/

# With verbose output
wav-to-ogg -v audio.wav

# Recursive directory processing
wav-to-ogg --recursive /path/to/audio/
```

### Development Tools
```bash
# Code formatting
uv run black wav_to_ogg/

# Import sorting
uv run isort wav_to_ogg/

# Linting
uv run flake8 wav_to_ogg/

# Type checking
uv run mypy wav_to_ogg/

# Run tests
uv run pytest

# Run all quality checks
uv run black wav_to_ogg/ && uv run isort wav_to_ogg/ && uv run flake8 wav_to_ogg/ && uv run mypy wav_to_ogg/
```

### Alternative Installation (pip-based)
If uv is not available, use pip with the pre-generated requirements.txt:
```bash
pip install -r requirements.txt
pip install -e .
```

## Important Notes

- The application converts files in-place (same directory as input) by default
- Requires ffmpeg to be installed on the system for audio processing
- Uses a CLI script entry point defined in pyproject.toml, run via `uv run wav-to-ogg`
- Supports both single file and batch directory processing
- Error handling and logging integrated throughout the application
- No longer uses Docker - runs directly on the host system

## Architecture Patterns

### CLI Design Pattern
The application follows a three-layer architecture:
1. **CLI Layer** (`cli.py`): Argument parsing, user interaction, and error handling
2. **Service Layer** (`converter.py`): Business logic for audio conversion
3. **Utility Layer** (`utils.py`): Common functions for validation, logging, and file operations

### Error Handling Strategy
- Path validation occurs at the CLI layer using `validate_input_path()`
- Audio conversion errors are caught and logged in the converter layer
- CLI returns appropriate exit codes (0=success, 1=error, 130=interrupted)

### Logging Configuration
- Centralized logging setup in `utils.py`
- Two-level logging: INFO for normal output, DEBUG for verbose mode
- Structured format with timestamps and module names

### Dependencies Management
- Core dependency: `pydub` for audio processing (requires ffmpeg)
- Dev dependencies: `black`, `isort`, `flake8`, `mypy`, `pytest`
- Python version constraint: >=3.8.1 for broad compatibility