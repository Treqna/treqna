# Release Management Guide

This document outlines the standard operating procedure for publishing a new release of Treqna.

## Release Prerequisites

- All unit tests pass cleanly: `python -m pytest`
- Static type checking passes cleanly: `python -m mypy src`
- Ruff linter and formatter pass cleanly: `python -m ruff check src`
- Version in `src/treqna/_version.py` updated according to Semantic Versioning (SemVer).
- `CHANGELOG.md` updated with release notes.

## Release Steps

1. Create a release branch:
   ```bash
   git checkout -b release/v0.1.0
   ```

2. Update `src/treqna/_version.py` and commit:
   ```bash
   git commit -m "chore: bump version to v0.1.0"
   ```

3. Tag the commit with signed tag:
   ```bash
   git tag -s v0.1.0 -m "Release v0.1.0"
   ```

4. Push tag to GitHub:
   ```bash
   git push origin v0.1.0
   ```

5. GitHub Actions workflow (`release.yml`) will build sdist/wheel and publish to PyPI automatically.
