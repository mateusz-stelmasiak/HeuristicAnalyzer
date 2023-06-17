import chess
import pandas as pd

from engines.Engine import Engine, EngineType


class SwineAnalyzer:

    def __init__(self, sf_depth_limit):
        self.board = chess.Board()
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
        return self.analytical_method(moves)

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

    def empirical_method(self, moves):
        board = chess.Board()
        for move in moves:
            board.push_uci(move)
            legal_moves = board.generate_legal_moves()
            print(legal_moves)
            rook_moves = [m for m in legal_moves if str(m)[1] == '7' and board.piece_at(m.from_square).symbol() == 'R'
                          or str(m)[1] == '2' and board.piece_at(m.from_square).symbol() == 'r']
            for rook_moves in legal_moves:
                print(f"Found possible rook move: {rook_moves}")

        # for move in moves:
        #     # Create a new chess.Board object from the current move list
        #     board = chess.Board()
        #     for m in moves:
        #         board.push_san(m)
        #
        #     # Generate a list of all legal moves
        #     legal_moves = list(board.legal_moves)
        #
        #     # Filter the moves to only include those where a rook moves to the 7th (or 2nd) rank
        #     rook_moves = [m for m in legal_moves if str(m)[1] == '7' and board.piece_at(m.from_square).symbol() == 'R'
        #                   or str(m)[1] == '2' and board.piece_at(m.from_square).symbol() == 'r']
        #
        #     # Use the engine to evaluate the rook moves
        #     for rook_move in rook_moves:
        #         result = self.engine.play(board, self.limit)
        #
        #         # If the move is the best one according to Stockfish
        #         if rook_move == result.move:
        #             if str(rook_move)[1] == '7':
        #                 self.results['WhiteSingleSwine'] = True
        #             else:  # str(rook_move)[1] == '2'
        #                 self.results['BlackSingleSwine'] = True
        #
        # return pd.DataFrame(self.results, index=[0])
