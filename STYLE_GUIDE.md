# Treqna Code Style Guide

This document defines the coding standards enforced across the Treqna repository.

## Rules

### 1. Zero-Comment Policy
- **NO inline comments (`# ...`)** are permitted in Python source code.
- **NO block comments (`# ...`)** are permitted in Python source code.
- **NO TODO or FIXME comments** are permitted in Python source code.
- Use descriptive variable names, function names, and complete type annotations to ensure code is self-documenting.

### 2. Static Typing
- All functions, methods, parameters, and return values MUST have explicit type annotations.
- Use Python 3.13+ standard library generics (`list[str]`, `dict[str, Any]`, `tuple[int, ...]`).
- Run `python -m mypy src` before committing code.

### 3. Formatting & Linting
- Code MUST pass `ruff check src` without errors or warnings.
- Maximum line length is 88 characters.
- Imports MUST be sorted alphabetically using standard `isort` ordering enforced by Ruff.

### 4. Dataclasses & Models
- All models, results, contexts, descriptors, and options MUST be immutable (`@dataclass(frozen=True, kw_only=True)`).
