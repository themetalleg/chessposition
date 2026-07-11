from __future__ import annotations

FILES = "abcdefgh"
RANKS = "87654321"
PIECE_TYPES = [("K", "King"), ("Q", "Queen"), ("R", "Rook"), ("B", "Bishop"), ("N", "Knight"), ("P", "Pawn")]
PIECE_CODES = {code for code, _ in PIECE_TYPES}
PIECE_SVG_FILES = {
    "K": "Chess_klt45.svg",
    "Q": "Chess_qlt45.svg",
    "R": "Chess_rlt45.svg",
    "B": "Chess_blt45.svg",
    "N": "Chess_nlt45.svg",
    "P": "Chess_plt45.svg",
    "k": "Chess_kdt45.svg",
    "q": "Chess_qdt45.svg",
    "r": "Chess_rdt45.svg",
    "b": "Chess_bdt45.svg",
    "n": "Chess_ndt45.svg",
    "p": "Chess_pdt45.svg",
}


def square_name(file_index: int, rank_index: int) -> str:
    return f"{FILES[file_index]}{RANKS[rank_index]}"
