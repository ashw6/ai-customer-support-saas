"""Centralized logging helpers for the API process."""
from __future__ import annotations

import logging


class RequestContextFilter(logging.Filter):
    """Allow log formatters to include request_id when present on the LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def configure_app_logging(*, level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s request_id=%(request_id)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        root.setLevel(level)
    for handler in root.handlers:
        handler.addFilter(RequestContextFilter())
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
