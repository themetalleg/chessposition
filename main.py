from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QPointF, Qt, QMimeData, Signal
from PySide6.QtGui import QAction, QColor, QDrag, QImage, QPainter, QPen, QPixmap, QTransform
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.logging_manager import LoggingManager
from core.style_manager import StyleManager
from fen_utils import board_to_fen
from utils.chess_utils import FILES, PIECE_CODES, PIECE_SVG_FILES, PIECE_TYPES, RANKS, square_name
logger = LoggingManager.get_logger(__name__)


@dataclass(frozen=True)
class SquareCoord:
    file_index: int
    rank_index: int

    @property
    def name(self) -> str:
        return square_name(self.file_index, self.rank_index)


class PieceIconStore:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], QPixmap] = {}
        self._svg_data: dict[str, bytes] = {}
        self._pieces_dir = Path(__file__).resolve().parent / "pieces"

    def pixmap(self, piece: str, size: int) -> QPixmap:
        key = (piece, size)
        if key in self._cache:
            return self._cache[key]
        pixmap = self._render_svg(piece, size)
        self._cache[key] = pixmap
        return pixmap

    def _render_svg(self, piece: str, size: int) -> QPixmap:
        data = self._svg_data.get(piece)
        if data is None:
            file_name = PIECE_SVG_FILES[piece]
            svg_path = self._pieces_dir / file_name
            try:
                data = svg_path.read_bytes()
                self._svg_data[piece] = data
            except Exception:
                logger.exception("Failed reading piece asset: %s", svg_path)
                data = b""
        if data:
            renderer = QSvgRenderer(data)
            if renderer.isValid():
                img = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
                img.fill(Qt.transparent)
                painter = QPainter(img)
                renderer.render(painter)
                painter.end()
                return QPixmap.fromImage(img)
            logger.warning("Invalid SVG data for piece '%s'; using fallback icon.", piece)
        fallback = QPixmap(size, size)
        fallback.fill(Qt.transparent)
        painter = QPainter(fallback)
        painter.setPen(Qt.white if piece.islower() else Qt.black)
        painter.drawText(fallback.rect(), Qt.AlignCenter, piece.upper())
        painter.end()
        return fallback


class PhotoCornerWidget(QLabel):
    cornersChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setMinimumSize(420, 420)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Load a photo and click 4 board corners (any order).")
        self._source_pixmap: QPixmap | None = None
        self._display_pixmap: QPixmap | None = None
        self._corners: list[QPointF] = []

    def set_photo(self, path: str) -> None:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            raise ValueError("Could not load image.")
        self._source_pixmap = pixmap
        self._corners.clear()
        self._refresh_view()
        self.cornersChanged.emit()

    def clear_corners(self) -> None:
        self._corners.clear()
        self._refresh_view()
        self.cornersChanged.emit()

    @property
    def source_pixmap(self) -> QPixmap | None:
        return self._source_pixmap

    @property
    def corners(self) -> list[QPointF]:
        return list(self._corners)

    def mousePressEvent(self, event) -> None:
        if self._source_pixmap is None or self._display_pixmap is None:
            return
        if event.button() != Qt.LeftButton:
            return
        if len(self._corners) == 4:
            self._corners.clear()
        point = self._map_to_source(event.position())
        if point is None:
            return
        self._corners.append(point)
        self._refresh_view()
        self.cornersChanged.emit()

    def _map_to_source(self, pos: QPointF) -> QPointF | None:
        if self._source_pixmap is None or self._display_pixmap is None:
            return None
        sx = self._display_pixmap.width() / self._source_pixmap.width()
        sy = self._display_pixmap.height() / self._source_pixmap.height()
        if sx == 0 or sy == 0:
            return None
        left = (self.width() - self._display_pixmap.width()) / 2
        top = (self.height() - self._display_pixmap.height()) / 2
        x = pos.x() - left
        y = pos.y() - top
        return QPointF(x / sx, y / sy)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_view()

    def _refresh_view(self) -> None:
        if self._source_pixmap is None:
            return
        scaled = self._source_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        canvas = QPixmap(self.size())
        canvas.fill(Qt.transparent)
        painter = QPainter(canvas)
        left = (canvas.width() - scaled.width()) / 2
        top = (canvas.height() - scaled.height()) / 2
        painter.drawPixmap(int(left), int(top), scaled)
        sx = scaled.width() / self._source_pixmap.width()
        sy = scaled.height() / self._source_pixmap.height()
        colors = [QColor("#50fa7b"), QColor("#8be9fd"), QColor("#ffb86c"), QColor("#ff79c6")]
        for i, source_point in enumerate(self._corners):
            p = QPointF(left + source_point.x() * sx, top + source_point.y() * sy)
            painter.setPen(colors[i % len(colors)])
            painter.setBrush(colors[i % len(colors)])
            painter.drawEllipse(p, 5, 5)
            painter.drawText(p + QPointF(8, -8), str(i + 1))
        painter.end()
        self._display_pixmap = scaled
        self.setPixmap(canvas)


class PiecePaletteItem(QLabel):
    def __init__(self, code: str, name: str, icon_store: PieceIconStore, palette: "PiecePalette") -> None:
        super().__init__()
        self._code = code
        self._icon_store = icon_store
        self._palette = palette
        self.setToolTip(name)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(66, 66)
        self.update_icon("white")

    def update_icon(self, color: str) -> None:
        piece = self._code if color == "white" else self._code.lower()
        self.setPixmap(self._icon_store.pixmap(piece, 56))

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.LeftButton:
            return
        mime_data = QMimeData()
        mime_data.setText(self._code)
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        piece = self._code if self._palette._active_color == "white" else self._code.lower()
        drag.setPixmap(self._icon_store.pixmap(piece, 48))
        self._palette.pieceDragStarted.emit(self._code)
        drag.exec(Qt.CopyAction)


class PiecePalette(QWidget):
    pieceDragStarted = Signal(str)

    def __init__(self, icon_store: PieceIconStore) -> None:
        super().__init__()
        self.setMaximumWidth(170)
        self._active_color = "white"
        self._items: list[PiecePaletteItem] = []
        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        for code, name in PIECE_TYPES:
            item = PiecePaletteItem(code, name, icon_store, self)
            self._items.append(item)
        for index, item in enumerate(self._items):
            row = index // 3
            col = index % 3
            layout.addWidget(item, row, col)

    def set_active_color(self, color: str) -> None:
        self._active_color = color
        for item in self._items:
            item.update_icon(color)


class BoardWidget(QWidget):
    boardChanged = Signal()

    def __init__(self, icon_store: PieceIconStore) -> None:
        super().__init__()
        self.setMinimumSize(500, 500)
        self.setAcceptDrops(True)
        self._icon_store = icon_store
        self._board: dict[str, str] = {}
        self._overlay: QPixmap | None = None
        self.active_color = "white"

    def board_state(self) -> dict[str, str]:
        return dict(self._board)

    def set_overlay(self, pixmap: QPixmap | None) -> None:
        self._overlay = pixmap
        self.update()

    def set_active_color(self, color: str) -> None:
        self.active_color = color

    def clear_board(self) -> None:
        self._board.clear()
        self.boardChanged.emit()
        self.update()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        piece_type = event.mimeData().text().strip().upper()
        square = self._square_at(event.position())
        if square is None or piece_type not in PIECE_CODES:
            return
        self._board[square.name] = piece_type if self.active_color == "white" else piece_type.lower()
        self.boardChanged.emit()
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.RightButton:
            square = self._square_at(event.position())
            if square is None:
                return
            menu = QMenu(self)
            for code, name in PIECE_TYPES:
                action = QAction(name, self)
                action.triggered.connect(
                    lambda checked=False, c=code, s=square.name: self._place_piece(
                        s, c if self.active_color == "white" else c.lower()
                    )
                )
                menu.addAction(action)
            menu.addSeparator()
            clear_action = QAction("Clear square", self)
            clear_action.triggered.connect(lambda checked=False, s=square.name: self._clear_square(s))
            menu.addAction(clear_action)
            menu.exec(event.globalPos())

    def _place_piece(self, square: str, piece: str) -> None:
        self._board[square] = piece
        self.boardChanged.emit()
        self.update()

    def _clear_square(self, square: str) -> None:
        self._board.pop(square, None)
        self.boardChanged.emit()
        self.update()

    def _square_at(self, pos: QPointF) -> SquareCoord | None:
        side = min(self.width(), self.height())
        origin_x = (self.width() - side) / 2
        origin_y = (self.height() - side) / 2
        if not (origin_x <= pos.x() <= origin_x + side and origin_y <= pos.y() <= origin_y + side):
            return None
        square_size = side / 8
        file_index = int((pos.x() - origin_x) / square_size)
        rank_index = int((pos.y() - origin_y) / square_size)
        if 0 <= file_index < 8 and 0 <= rank_index < 8:
            return SquareCoord(file_index, rank_index)
        return None

    def paintEvent(self, event) -> None:
        side = min(self.width(), self.height())
        origin_x = int((self.width() - side) / 2)
        origin_y = int((self.height() - side) / 2)
        square_size = side / 8
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1e1f29"))
        if self._overlay is not None:
            painter.setOpacity(1.0)
            painter.drawPixmap(origin_x, origin_y, side, side, self._overlay)
            painter.setOpacity(1.0)
        light = QColor("#ffffff")
        light.setAlphaF(0.3)
        for rank in range(8):
            for file_index in range(8):
                if (rank + file_index) % 2 != 0:
                    continue
                x = int(origin_x + file_index * square_size)
                y = int(origin_y + rank * square_size)
                painter.fillRect(x, y, int(square_size) + 1, int(square_size) + 1, light)
        grid_pen = QPen(QColor("#ff0000"))
        grid_pen.setWidth(max(2, int(square_size * 0.08)))
        painter.setPen(grid_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(origin_x, origin_y, side, side)
        for i in range(1, 8):
            x = int(origin_x + i * square_size)
            y = int(origin_y + i * square_size)
            painter.drawLine(x, origin_y, x, origin_y + side)
            painter.drawLine(origin_x, y, origin_x + side, y)
        for rank_index, rank in enumerate(RANKS):
            for file_index, file_name in enumerate(FILES):
                square = f"{file_name}{rank}"
                piece = self._board.get(square)
                if not piece:
                    continue
                pix = self._icon_store.pixmap(piece, int(square_size * 0.85))
                x = int(origin_x + file_index * square_size + (square_size - pix.width()) / 2)
                y = int(origin_y + rank_index * square_size + (square_size - pix.height()) / 2)
                painter.drawPixmap(x, y, pix)
        painter.end()


class CopyableFenLabel(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            fen = self.text().strip()
            if fen:
                QApplication.clipboard().setText(fen)
                logger.info("FEN copied to clipboard.")
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Chess Position from Photo")
        self.resize(1200, 760)
        self._icons = PieceIconStore()
        self.photo_widget = PhotoCornerWidget()
        self.palette = PiecePalette(self._icons)
        self.board = BoardWidget(self._icons)
        self.fen_label = CopyableFenLabel()
        self._build_ui()
        self._connect_signals()
        self._update_fen()

    def _build_ui(self) -> None:
        outer = QWidget()
        root = QVBoxLayout(outer)

        toolbar = QHBoxLayout()
        self.load_btn = QPushButton("Load photo")
        self.reset_corners_btn = QPushButton("Reset corners")
        self.clear_board_btn = QPushButton("Clear board")
        toolbar.addWidget(self.load_btn)
        toolbar.addWidget(self.reset_corners_btn)
        toolbar.addWidget(self.clear_board_btn)
        toolbar.addStretch()
        color_group = QGroupBox("Right-click / drag color")
        colors_layout = QHBoxLayout(color_group)
        self.white_radio = QRadioButton("White")
        self.black_radio = QRadioButton("Black")
        self.white_radio.setChecked(True)
        self.color_buttons = QButtonGroup(self)
        self.color_buttons.addButton(self.white_radio)
        self.color_buttons.addButton(self.black_radio)
        colors_layout.addWidget(self.white_radio)
        colors_layout.addWidget(self.black_radio)
        toolbar.addWidget(color_group)
        root.addLayout(toolbar)

        splitter = QSplitter()
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Photo corner marking"))
        left_layout.addWidget(self.photo_widget, stretch=1)
        left_layout.addWidget(QLabel("Piece palette (drag to board)"))
        left_layout.addWidget(self.palette)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.board)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, stretch=1)

        root.addWidget(self.fen_label)
        self.setCentralWidget(outer)

    def _connect_signals(self) -> None:
        self.load_btn.clicked.connect(self._load_photo)
        self.reset_corners_btn.clicked.connect(self.photo_widget.clear_corners)
        self.photo_widget.cornersChanged.connect(self._warp_photo)
        self.clear_board_btn.clicked.connect(self.board.clear_board)
        self.board.boardChanged.connect(self._update_fen)
        self.white_radio.toggled.connect(
            lambda checked: self._set_active_color("white" if checked else "black")
        )
        self._set_active_color("white")

    def _set_active_color(self, color: str) -> None:
        self.board.set_active_color(color)
        self.palette.set_active_color(color)

    def _load_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open board photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return
        try:
            self.photo_widget.set_photo(path)
        except ValueError as error:
            QMessageBox.warning(self, "Photo error", str(error))

    def _warp_photo(self) -> None:
        source = self.photo_widget.source_pixmap
        corners = self.photo_widget.corners
        if source is None:
            self.board.set_overlay(None)
            return
        if len(corners) != 4:
            self.board.set_overlay(None)
            return
        src = self._order_corners(corners)
        side = 1024
        dst = [QPointF(0, 0), QPointF(side, 0), QPointF(side, side), QPointF(0, side)]
        transform = self._quad_to_quad_transform(src, dst)
        if transform is None:
            logger.warning("Warp transform could not be computed for selected corners.")
            QMessageBox.warning(self, "Transform error", "Could not compute board transform.")
            return
        warped = QPixmap(side, side)
        warped.fill(Qt.transparent)
        painter = QPainter(warped)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setTransform(transform)
        painter.drawPixmap(0, 0, source)
        painter.end()
        self.board.set_overlay(warped)
        logger.info("Warp overlay applied.")

    @staticmethod
    def _order_corners(corners: list[QPointF]) -> list[QPointF]:
        points = [QPointF(p.x(), p.y()) for p in corners]
        sums = [p.x() + p.y() for p in points]
        diffs = [p.y() - p.x() for p in points]
        top_left = points[sums.index(min(sums))]
        bottom_right = points[sums.index(max(sums))]
        top_right = points[diffs.index(min(diffs))]
        bottom_left = points[diffs.index(max(diffs))]
        return [top_left, top_right, bottom_right, bottom_left]

    @staticmethod
    def _quad_to_quad_transform(src: list[QPointF], dst: list[QPointF]) -> QTransform | None:
        try:
            result = QTransform.quadToQuad(src, dst)
            if isinstance(result, tuple):
                ok, transform = result
                return transform if ok else None
        except TypeError:
            pass
        try:
            transform = QTransform()
            ok = QTransform.quadToQuad(src, dst, transform)
            return transform if ok else None
        except TypeError:
            return None

    def _update_fen(self) -> None:
        self.fen_label.setText(board_to_fen(self.board.board_state()))


def main() -> int:
    LoggingManager.configure()
    app = QApplication(sys.argv)
    StyleManager().apply_theme(app)
    window = MainWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
