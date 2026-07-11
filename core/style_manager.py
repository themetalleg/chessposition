from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.logging_manager import LoggingManager


class StyleManager:
    def __init__(self, styles_dir: Path | None = None) -> None:
        self._styles_dir = styles_dir or Path(__file__).resolve().parent.parent / "styles"
        self._logger = LoggingManager.get_logger(__name__)

    def apply_theme(self, app: QApplication, qss_file: str = "dark.qss") -> bool:
        app.setStyle("Fusion")
        style_path = self._styles_dir / qss_file
        if not style_path.exists():
            self._logger.warning("QSS file not found: %s", style_path)
            return False
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))
        self._logger.info("Applied stylesheet: %s", style_path)
        return True
