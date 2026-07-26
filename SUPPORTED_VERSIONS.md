# Supported Versions Policy

This document outlines the Python runtime versions supported by Treqna.

## Python Runtime Support Matrix

| Python Version | Support Status | Minimum Treqna Version | Notes |
| --- | --- | --- | --- |
| Python 3.13 | Primary | 0.1.0 | Recommended for production |
| Python 3.12 | Supported | 0.1.0 | Fully tested in CI |
| Python 3.11 | Supported | 0.1.0 | Minimum supported Python version |
| Python < 3.11 | End of Life | N/A | Not supported |

## Lifecycle Schedule

Treqna aligns its Python version support window with the official Python release lifecycle defined in PEP 602. When a Python version reaches End of Life (EOL) upstream, Treqna will deprecate support in the subsequent minor release.
