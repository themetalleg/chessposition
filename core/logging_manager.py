from __future__ import annotations

import logging


class LoggingManager:
    _configured = False

    @classmethod
    def configure(cls, level: int = logging.INFO) -> None:
        if cls._configured:
            return
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
        root = logging.getLogger()
        root.setLevel(level)
        root.addHandler(handler)
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)
