# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an audio conversion tool that converts WAV files to OGG format using Python and uv for package management. It ships both a command-line interface and an optional drag-and-drop GUI, and supports single file conversion and batch processing of directories.

## Architecture

The project follows a modular CLI architecture, with an optional GUI presentation layer alongside it:
- **CLI Module (`wav_to_ogg/cli.py`)**: Command-line interface with argument parsing
- **Converter Module (`wav_to_ogg/converter.py`)**: Core audio conversion logic using pydub
- **Utils Module (`wav_to_ogg/utils.py`)**: Utility functions for logging, validation, and file operations
- **Package Init (`wav_to_ogg/__init__.py`)**: Package initialization and version info
- **GUI Package (`wav_to_ogg/gui/`)**: Optional Tkinter-based drag-and-drop GUI (requires the `gui` extra); reuses `AudioConverter` and never modifies the CLI/converter/utils modules

## Key Components

- `wav_to_ogg/cli.py`: Command-line interface and main entry point
- `wav_to_ogg/converter.py`: AudioConverter class handling file/directory conversion
- `wav_to_ogg/utils.py`: Utility functions for logging, validation, and file operations
- `wav_to_ogg/gui/dnd.py`: Parses tkinterdnd2 drop event payloads into paths (no tkinter dependency)
- `wav_to_ogg/gui/model.py`: Immutable `FileQueue` state for the file list (no tkinter dependency)
- `wav_to_ogg/gui/events.py`: Conversion progress event dataclasses (no tkinter dependency)
- `wav_to_ogg/gui/service.py`: `ConversionService` runs `AudioConverter` on a background thread and reports progress via a queue (no tkinter dependency)
- `wav_to_ogg/gui/app.py`: Tkinter view (`WavToOggApp`) — widgets and event wiring only, no business logic
- `wav_to_ogg/gui/__main__.py`: GUI entry point (`wav-to-ogg-gui`), handles missing `tkinterdnd2`/`ffmpeg` gracefully
- `pyproject.toml`: Project metadata and dependencies (PEP 621, managed with uv)
- `uv.lock`: Dependency lock file
- `requirements.txt`: pip-compatible dependency list

## Development Commands

### Setup and Installation
```bash
# Install dependencies with uv (recommended)
uv sync

# Include the optional GUI dependency (tkinterdnd2)
uv sync --extra gui

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

# Launch the drag-and-drop GUI (requires: uv sync --extra gui)
wav-to-ogg-gui
```

### Development Tools
```bash
# Code formatting
uv run black wav_to_ogg/

# Import sorting
uv run isort wav_to_ogg/

# Linting
uv run flake8 wav_to_ogg/

# Type checking (use --extra gui so tkinterdnd2 is resolvable)
uv run --extra gui mypy wav_to_ogg/

# Run tests (includes GUI unit tests and a GUI smoke test)
uv run --extra gui pytest

# Run all quality checks
uv run black wav_to_ogg/ && uv run isort wav_to_ogg/ && uv run flake8 wav_to_ogg/ && uv run --extra gui mypy wav_to_ogg/
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
- Uses CLI and GUI script entry points defined in pyproject.toml, run via `uv run wav-to-ogg` and `uv run wav-to-ogg-gui`
- Supports both single file and batch directory processing
- Error handling and logging integrated throughout the application
- No longer uses Docker - runs directly on the host system
- The GUI is an optional feature (`gui` extra): missing `tkinterdnd2` or a missing `ffmpeg` binary produce a logged error/warning instead of crashing

## Architecture Patterns

### CLI Design Pattern
The application follows a three-layer architecture:
1. **CLI Layer** (`cli.py`): Argument parsing, user interaction, and error handling
2. **Service Layer** (`converter.py`): Business logic for audio conversion
3. **Utility Layer** (`utils.py`): Common functions for validation, logging, and file operations

### GUI Design Pattern
The GUI mirrors the same separation, keeping tkinter isolated from logic so most of it is unit-testable:
1. **View Layer** (`gui/app.py`, `gui/__main__.py`): Tkinter widgets, drag-and-drop wiring, entry point — no business logic
2. **Logic Layer** (`gui/dnd.py`, `gui/model.py`, `gui/events.py`, `gui/service.py`): Pure Python, no tkinter import, fully covered by `tests/unit/`
3. Conversion runs on a background `threading.Thread` via `ConversionService`; the Tk main loop polls a `queue.Queue` with `root.after()` so the UI never blocks and Tk widgets are only touched from the main thread

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
- Optional `gui` extra: `tkinterdnd2` for drag-and-drop file support on top of the standard library `tkinter`
- Dev dependencies: `black`, `isort`, `flake8`, `mypy`, `pytest`
- Python version constraint: >=3.8.1 for broad compatibility