# chessposition

Desktop app to build a chess position from a photo and export FEN notation.

## Features

- PySide6 desktop GUI with dark mode.
- Load a board photo, click the 4 board corners, and warp the photo to a square virtual board background.
- Place pieces by:
  - Dragging from the side piece palette.
  - Right-clicking a square and choosing a piece from a context menu.
- White/Black switch controls which color is placed by drag and right-click.
- Live FEN generation.
- Piece images come from Wikimedia Commons SVG set:
  - https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces

## Run

```bash
python -m pip install -r requirements.txt
python /home/runner/work/chessposition/chessposition/app.py
```

## Test

```bash
python -m unittest discover -v
```
