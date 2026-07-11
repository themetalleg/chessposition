# Photo2LEN

Desktop app to build a chess position from a photo and export FEN notation.

## Features

- PySide6 desktop GUI with dark mode.
- Left-click photo area to load a photo if empty.
- Right-click photo area to open upload dialog at any time.
- With a loaded photo, left-click 4 board corners (in any order); once all four are set, the photo is warped automatically to the board background.
- Corner points can be placed outside the visible photo area for cut-off photos.
- Place pieces by:
  - Dragging from the bottom piece palette.
  - Dragging already-placed pieces to other squares.
  - Right-clicking a square and choosing a piece from a context menu.
- Board right-click menu also includes clear square and clear board actions.
- White/Black switch controls which color is placed by drag and right-click.
- App opens maximized.
- Live FEN generation shown centered at the bottom; click the FEN text to copy it.
- After copy, `Copied` is appended to the FEN text for 5 seconds, then removed.
- A live Lichess analysis link is shown below the FEN and updates with the current position.
- Piece images come from Wikimedia Commons SVG set:
  - https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces

## Run

```bash
python -m pip install -r requirements.txt
python /home/runner/work/chessposition/chessposition/main.py
```

### VS Code task

Use the included VS Code task:

- Task label: `▶️ Run`
- It runs `python -B ${workspaceFolder}/main.py` with `PYTHONDONTWRITEBYTECODE=1` (no `.pyc` cache files written).

## Test

```bash
python -m unittest discover -s tests -q
```
