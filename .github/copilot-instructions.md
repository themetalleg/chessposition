Project structure and architecture guidance:

- Entrypoint: `/home/runner/work/chessposition/chessposition/main.py`
- Core services live in `/home/runner/work/chessposition/chessposition/core/`
  - Use `core.logging_manager.LoggingManager` for logging setup and logger access.
  - Use `core.style_manager.StyleManager` to load and apply QSS themes.
- Shared helpers/constants live in `/home/runner/work/chessposition/chessposition/utils/`
  - Use `utils.chess_utils` for board/file/rank and piece metadata helpers.
  - Use `utils.fen_utils` for FEN serialization (`board_to_fen`).
- Keep Qt styling centralized in `/home/runner/work/chessposition/chessposition/styles/`.
  - Use `styles/dark.qss` for widget styling.
  - Use `styles/colors.py` for drawing colors used by custom-painted widgets.
- Avoid adding inline widget styles or hardcoded color literals in Python files when changing app appearance.

Current UI behavior to preserve:
- App opens maximized.
- Top row has photo area (left) and board area (right), intended to stay equal height.
- Photo interactions:
  - Left-click loads photo if empty; otherwise sets corner markers.
  - Right-click opens upload dialog.
  - After 4 corners, next left-click restarts corner marking.
  - Corner order is auto-detected for warp orientation.
- Warp applies automatically once 4 corners are marked.
- Bottom row contains 6 piece icons in one line, plus a circle-only color toggle (⚪/⚫).
- Board supports drag/drop from palette and dragging already-placed pieces.
- Board right-click menu supports place piece, clear square, and clear board.
- FEN is displayed centered at bottom and copied on click.
