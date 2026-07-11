from __future__ import annotations

from typing import Mapping

FILES = "abcdefgh"
RANKS = "87654321"
VALID_PIECES = set("KQRBNPkqrbnp")


def board_to_fen(board: Mapping[str, str]) -> str:
    rows: list[str] = []
    for rank in RANKS:
        empty = 0
        row: list[str] = []
        for file_name in FILES:
            square = f"{file_name}{rank}"
            piece = board.get(square)
            if not piece:
                empty += 1
                continue
            if piece not in VALID_PIECES:
                raise ValueError(f"Invalid piece on {square}: {piece!r}")
            if empty:
                row.append(str(empty))
                empty = 0
            row.append(piece)
        if empty:
            row.append(str(empty))
        rows.append("".join(row))
    return "/".join(rows)
