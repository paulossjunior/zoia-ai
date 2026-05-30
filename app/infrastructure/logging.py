"""Logging setup shared by the API and worker entrypoints."""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    """Configure process-wide logging for command submission and processing."""
    level = logging.DEBUG if os.getenv("APP_ENV") == "local" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
