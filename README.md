# chessposition

Desktop app to build a chess position from a photo and export FEN notation.

## Features

- PySide6 desktop GUI with dark mode.
- Load a board photo and click 4 board corners (in any order); once all four are set, the photo is warped automatically to the board background.
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
python /home/runner/work/chessposition/chessposition/main.py
```

## Test

```bash
python -m unittest discover -v
```
