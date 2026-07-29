import os
import sys
from pathlib import Path


def ensure_directory(path: Path | str) -> Path:
    target_path = Path(path).resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    return target_path


def get_environment_variable(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def get_platform_info() -> dict[str, str]:
    return {
        "python_version": sys.version,
        "platform": sys.platform,
    }
