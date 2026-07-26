import logging
import sys
from typing import Final, TextIO

DEFAULT_LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def get_logger(name: str = "treqna") -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(
    level: str | int = "INFO",
    log_format: str = DEFAULT_LOG_FORMAT,
    stream: TextIO | None = None,
) -> logging.Logger:
    logger = get_logger()
    target_stream = stream if stream is not None else sys.stdout

    if isinstance(level, str):
        numeric_level = logging.getLevelName(level.upper())
        if not isinstance(numeric_level, int):
            numeric_level = logging.INFO
    else:
        numeric_level = level

    logger.setLevel(numeric_level)
    logger.handlers.clear()

    handler = logging.StreamHandler(target_stream)
    handler.setLevel(numeric_level)

    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

