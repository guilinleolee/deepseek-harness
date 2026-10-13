"""Kernel diagnostics: stderr only, never stdout (stdout carries the protocol)."""

import os
import sys

LEVELS = {"TRACE": 0, "DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40, "FATAL": 50}


def _threshold() -> int:
    """The active level threshold; `QUANT_KERNEL_LOG_LEVEL` raises verbosity in the field."""
    raw = os.environ.get("QUANT_KERNEL_LOG_LEVEL", "ERROR").upper()
    return LEVELS.get(raw, LEVELS["ERROR"])


def _emit(level: str, message: str) -> None:
    """Write one diagnostic line to stderr when the level is enabled."""
    if LEVELS[level] >= _threshold():
        sys.stderr.write(f"[quant-kernel][{level}] {message}\n")
        sys.stderr.flush()


def log_debug(message: str) -> None:
    """Emit a DEBUG diagnostic (data pulls, cache hits)."""
    _emit("DEBUG", message)


def log_error(message: str) -> None:
    """Emit an ERROR diagnostic (handler failures, protocol errors)."""
    _emit("ERROR", message)
