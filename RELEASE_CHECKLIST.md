# Treqna GitHub & PyPI Release Checklist

Follow this pre-flight checklist before pressing the **Publish** button on GitHub or releasing to PyPI.

---

## 1. Pre-Flight Verification

- [x] **Static Type Check**: Run `python -m mypy src` (0 errors).
- [x] **Linting & Code Formatting**: Run `python -m ruff check src` (0 warnings).
- [x] **Test Suite**: Run `python -m pytest` (172 tests passing).
- [x] **Transformation Matrix**: Run `python -m pytest tests/integration/test_compatibility_matrix.py` (25 format pairs passing).
- [x] **Documentation Build**: Run `mkdocs build` (0 warnings).
- [x] **Dependencies Audit**: Verify zero external runtime dependencies in `pyproject.toml`.

---

## 2. Versioning & Tags

- [x] Version `0.1.0` verified in `pyproject.toml` and `src/treqna/_version.py`.
- [x] `CHANGELOG.md` updated with release notes for `v0.1.0`.

---

## 3. GitHub Release Steps

1. Push local `main` branch to remote repository:
   ```bash
   git push origin main
   ```
2. Create and push signed git tag `v0.1.0`:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```
3. Create GitHub Release from tag `v0.1.0`:
   - Set Title: `Treqna v0.1.0 - Initial Public Release`
   - Paste release notes from `CHANGELOG.md`.

---

## 4. PyPI Publishing Steps

1. Build source distribution and wheel:
   ```bash
   python -m pip install --upgrade build twine
   python -m build
   ```
2. Check built artifacts:
   ```bash
   twine check dist/*
   ```
3. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```
