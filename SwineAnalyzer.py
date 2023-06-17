import chess
import pandas as pd

from engines.Engine import Engine, EngineType


class SwineAnalyzer:

    def __init__(self, sf_depth_limit):
        #self.board = chess.Board()
        self.engine = Engine(EngineType.STOCKFISH)
        self.limit = chess.engine.Limit(depth=sf_depth_limit)

        self.current_positions = {
            'whiteKing': 'e1', 'blackKing': 'e8',
            'whiteRooka': 'a1', 'whiteRookh': 'h1',
            'blackRooka': 'a8', 'blackRookh': 'h8'
        }

        self.results = {
            'WhiteSingleSwine': False,
            'WhiteDoubleSwine': False,
            'BlackSingleSwine': False,
            'BlackDoubleSwine': False
        }

    def analyze_game(self, moves):
        return self.empirical_method(moves)

    def analytical_method(self, moves):
        for move in moves:
            move_from = move[:2]
            move_to = move[2:]

            # Check if a tracked piece is captured
            for piece, position in list(self.current_positions.items()):
                if position == move_to:
                    del self.current_positions[piece]

            # Kingside castling
            if move == 'e1g1' and 'whiteKing' in self.current_positions and self.current_positions['whiteKing'] == 'e1':
                self.current_positions['whiteRookh'] = 'f1'
                self.current_positions['whiteKing'] = 'g1'
            elif move == 'e8g8' and 'blackKing' in self.current_positions and self.current_positions[
                'blackKing'] == 'e8':
                self.current_positions['blackRookh'] = 'f8'
                self.current_positions['blackKing'] = 'g8'

            # Queenside castling
            elif move == 'e1c1' and 'whiteKing' in self.current_positions and self.current_positions[
                'whiteKing'] == 'e1':
                self.current_positions['whiteRooka'] = 'd1'
                self.current_positions['whiteKing'] = 'c1'
            elif move == 'e8c8' and 'blackKing' in self.current_positions and self.current_positions[
                'blackKing'] == 'e8':
                self.current_positions['blackRooka'] = 'd8'
                self.current_positions['blackKing'] = 'c8'

            # If a rook or king moved, update its position
            else:
                for piece, position in self.current_positions.items():
                    if move_from == position:
                        self.current_positions[piece] = move_to

                        if '7' in move_to and piece in ['whiteRooka', 'whiteRookh']:
                            self.results['WhiteSingleSwine'] = True
                            if '7' in self.current_positions.get('whiteRooka',
                                                                 '') and '7' in self.current_positions.get('whiteRookh',
                                                                                                           ''):
                                self.results['WhiteDoubleSwine'] = True

                        if '2' in move_to and piece in ['blackRooka', 'blackRookh']:
                            self.results['BlackSingleSwine'] = True
                            if '2' in self.current_positions.get('blackRooka',
                                                                 '') and '2' in self.current_positions.get('blackRookh',
                                                                                                           ''):
                                self.results['BlackDoubleSwine'] = True
            # optimisation conditions
            # if both player swined
            if self.results['WhiteDoubleSwine'] and self.results['BlackDoubleSwine']:
                break
            # if all rooks are taken
            if not any(rook in self.current_positions for rook in
                       ['whiteRooka', 'whiteRookh', 'blackRooka', 'blackRookh']):
                break

            # For white rooks - if one rook was taken and
            if (sum(rook in self.current_positions for rook in ['whiteRooka', 'whiteRookh']) == 1 and self.results[
                'WhiteSingleSwine']) and (
                    sum(rook in self.current_positions for rook in ['blackRooka', 'blackRookh']) == 1 and self.results[
                'BlackSingleSwine']):
                break

        return pd.DataFrame(self.results, index=[0])

    def empirical_method(self, moves): # i think it doesnt work, but checking this might not have much sense
        board = chess.Board()

        # Initialize the result
        result = {
            "WhiteSwineBestMoveCount": 0,
            "WhiteSwineNonBestMoveCount": 0,
            "BlackSwineBestMoveCount": 0,
            "BlackSwineNonBestMoveCount": 0,
        }

        for move in moves:
            board.push_uci(move)
            legal_moves = board.generate_legal_moves()

            rook_moves = [m for m in legal_moves if str(m)[1] == '7' and board.piece_at(m.from_square).symbol() == 'R'
                          or str(m)[1] == '2' and board.piece_at(m.from_square).symbol() == 'r']

            # Check if rook can move to 7th or 2nd rank.
            if rook_moves:
                # Get the best move
                best_move = self.engine.get_best_move(board, self.limit)

                # Check the color of the player
                if board.turn:
                    player_color = "White"
                else:
                    player_color = "Black"

                # If the best move is in rook_moves, increment best move count, else non-best move count.
                if best_move in rook_moves:
                    result[f"{player_color}SwineBestMoveCount"] += 1
                else:
                    result[f"{player_color}SwineNonBestMoveCount"] += 1

        return pd.DataFrame(result, index=[0])