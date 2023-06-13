import pandas as pd


class DevelopingAnalyzer:

    def __init__(self):
        self.pieces = {'b1': 'WhiteKnight_b1', 'g1': 'WhiteKnight_g1', 'c1': 'WhiteBishop_c1', 'f1': 'WhiteBishop_f1',
                       'b8': 'BlackKnight_b8', 'g8': 'BlackKnight_g8', 'c8': 'BlackBishop_c8', 'f8': 'BlackBishop_f8'}

    def analyze_game(self, moves):
        piece_moves = {k: 0 for k in self.pieces.keys()}
        for idx, move in enumerate(moves):
            move_from = move[:2]
            if move_from in piece_moves and piece_moves[move_from] == 0:
                piece_moves[move_from] = (idx // 2) + 1
        result_dict = {self.pieces[k]: v for k, v in piece_moves.items()}
        return pd.DataFrame(result_dict, index=[0])