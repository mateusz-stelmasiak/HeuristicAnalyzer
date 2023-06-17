import pandas as pd


class SwineAnalyzer:

    def __init__(self, sf_depth_limit):
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

        return pd.DataFrame(self.results, index=[0])
