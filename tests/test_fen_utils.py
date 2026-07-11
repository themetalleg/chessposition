import unittest

from utils.fen_utils import board_to_fen


class BoardToFenTests(unittest.TestCase):
    def test_empty_board(self):
        self.assertEqual(board_to_fen({}), "8/8/8/8/8/8/8/8")

    def test_start_position_pieces(self):
        board = {
            "a8": "r",
            "b8": "n",
            "c8": "b",
            "d8": "q",
            "e8": "k",
            "f8": "b",
            "g8": "n",
            "h8": "r",
            "a7": "p",
            "h7": "p",
            "a2": "P",
            "h2": "P",
            "a1": "R",
            "b1": "N",
            "c1": "B",
            "d1": "Q",
            "e1": "K",
            "f1": "B",
            "g1": "N",
            "h1": "R",
        }
        self.assertEqual(board_to_fen(board), "rnbqkbnr/p6p/8/8/8/8/P6P/RNBQKBNR")

    def test_invalid_piece_raises(self):
        with self.assertRaises(ValueError):
            board_to_fen({"e4": "X"})


if __name__ == "__main__":
    unittest.main()
