# Contributing to Treqna

Thank you for your interest in contributing to Treqna! This document outlines our development workflow, coding standards, and submission guidelines.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/treqna/treqna.git
   cd treqna
   ```

2. Create a virtual environment and install editable package:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .[dev]
   ```

## Development Workflow

Before submitting a pull request, run the complete verification suite:

```bash
# Static type checking
python -m mypy src

# Code linting
python -m ruff check src

# Unit and benchmark test suite
python -m pytest
```

## Pull Request Guidelines

1. Ensure all code strictly adheres to the [Zero-Comment Policy](STYLE_GUIDE.md).
2. Include complete type annotations for all new code.
3. Add unit tests in `tests/unit/` covering new features or bug fixes.
4. Ensure test coverage remains above 95%.
5. Follow the template provided in `.github/PULL_REQUEST_TEMPLATE.md`.
