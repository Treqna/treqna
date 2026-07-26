# Developer Guide

This guide describes how to work with the Treqna codebase as a developer.

## Project Structure

```
src/treqna/
├── __init__.py
├── __main__.py
├── _version.py
├── api/
├── cli/
├── config.py
├── core/
├── exceptions.py
├── logging.py
├── models/
├── plugins/
├── py.typed
├── registry/
├── typing/
└── utilities/
```

## Adding a Plugin Interface

All new plugin interfaces must be defined under `treqna.plugins.interface` and inherit from `PluginInterface`.

## Verification Commands

- `pytest`
- `mypy src`
- `ruff check src`
- `ruff format src`
