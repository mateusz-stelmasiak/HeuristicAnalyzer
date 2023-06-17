import chess
import pandas as pd

from engines.Engine import Engine, EngineType


class DevelopingAnalyzer:

    def __init__(self, sf_depth_limit):
        self.pieces = {'b1': 'WhiteKnight_b1', 'g1': 'WhiteKnight_g1', 'c1': 'WhiteBishop_c1', 'f1': 'WhiteBishop_f1',
                       'b8': 'BlackKnight_b8', 'g8': 'BlackKnight_g8', 'c8': 'BlackBishop_c8', 'f8': 'BlackBishop_f8'}
        self.board = chess.Board()
        self.engine = Engine(EngineType.STOCKFISH)
        self.limit = chess.engine.Limit(depth=sf_depth_limit)

    def analyze_game(self, moves):
        return self.empirical_method(moves)

    def analytical_method(self, moves):
        piece_moves = {k: 0 for k in self.pieces.keys()}
        moved_count = 0
        for idx, move in enumerate(moves):
            move_from = move[:2]
            if move_from in piece_moves and piece_moves[move_from] == 0:
                piece_moves[move_from] = (idx // 2) + 1
                moved_count += 1
                if moved_count == len(self.pieces):
                    break
        result_dict = {self.pieces[k]: v for k, v in piece_moves.items()}
        return pd.DataFrame(result_dict, index=[0])

    def empirical_method(self, moves):
        piece_moves = {k: 0 for k in self.pieces.keys()}
        board = chess.Board()

        best_piece_moves_count_white = 0
        best_piece_moves_count_black = 0
        considered_moves_white = 0
        considered_moves_black = 0

        for idx in range(min(len(moves), 20)):  # Go through all moves
            if not piece_moves:  # If all pieces have been developed, terminate the loop
                break

            legal_moves = [str(move)[:2] for move in board.legal_moves]
            piece_develop_moves_possible = any(
                move in piece_moves and board.piece_at(chess.SQUARE_NAMES.index(move)).symbol().lower() in 'bn' for
                move in legal_moves)

            if piece_develop_moves_possible:
                # Get the best move from the chess engine
                best_move = self.engine.get_best_move(board, self.limit)
                best_move_from = str(best_move)[:2]
                if board.turn:
                    considered_moves_white += 1
                    if best_move_from in piece_moves:
                        best_piece_moves_count_white += 1
                        del piece_moves[best_move_from]  # piece developed
                else:
                    considered_moves_black += 1
                    if best_move_from in piece_moves:
                        best_piece_moves_count_black += 1
                        del piece_moves[best_move_from]  # piece developed

            # Make the actual moves in the game

            board.push_uci(moves[idx])  # Make the move

        result_dict = {
            "ConsideredMovesWhite": considered_moves_white,
            "BestPieceMovesCountWhite": best_piece_moves_count_white,
            "ConsideredMovesBlack": considered_moves_black,
            "BestPieceMovesCountBlack": best_piece_moves_count_black
        }
        return pd.DataFrame(result_dict, index=[0])
