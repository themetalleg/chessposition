from __future__ import annotations

FILES = "abcdefgh"
RANKS = "87654321"
PIECE_TYPES = [("K", "King"), ("Q", "Queen"), ("R", "Rook"), ("B", "Bishop"), ("N", "Knight"), ("P", "Pawn")]
PIECE_CODES = {code for code, _ in PIECE_TYPES}
PIECE_SVG_FILES = {
    "K": "File_Chess_klt45.svg",
    "Q": "File_Chess_qlt45.svg",
    "R": "File_Chess_rlt45.svg",
    "B": "File_Chess_blt45.svg",
    "N": "File_Chess_nlt45.svg",
    "P": "File_Chess_plt45.svg",
    "k": "File_Chess_kdt45.svg",
    "q": "File_Chess_qdt45.svg",
    "r": "File_Chess_rdt45.svg",
    "b": "File_Chess_bdt45.svg",
    "n": "File_Chess_ndt45.svg",
    "p": "File_Chess_pdt45.svg",
}


def square_name(file_index: int, rank_index: int) -> str:
    return f"{FILES[file_index]}{RANKS[rank_index]}"
