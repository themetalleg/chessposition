Project structure and architecture guidance:

- Entrypoint: `/home/runner/work/chessposition/chessposition/main.py`
- Core services live in `/home/runner/work/chessposition/chessposition/core/`
  - Use `core.logging_manager.LoggingManager` for logging setup and logger access.
  - Use `core.style_manager.StyleManager` to load and apply QSS themes.
- Shared helpers/constants live in `/home/runner/work/chessposition/chessposition/utils/`
  - Use `utils.chess_utils` for board/file/rank and piece metadata helpers.
- Keep Qt styling centralized in `/home/runner/work/chessposition/chessposition/styles/`.
- Avoid adding inline widget styles in Python files when changing app appearance.
