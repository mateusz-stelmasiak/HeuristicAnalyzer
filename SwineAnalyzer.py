import pandas as pd

class SwineAnalyzer:

    def __init__(self, engine, limit):
        self.current_rook_positions = {
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
        for move in moves:
            move_from = move[:2]
            move_to = move[2:]

            # Kingside castling
            if move == 'e1g1':
                self.current_rook_positions['whiteRookh'] = 'f1'
            elif move == 'e8g8':
                self.current_rook_positions['blackRookh'] = 'f8'

            # Queenside castling
            elif move == 'e1c1':
                self.current_rook_positions['whiteRooka'] = 'd1'
            elif move == 'e8c8':
                self.current_rook_positions['blackRooka'] = 'd8'

            # If a rook moved, update its position
            else:
                for rook, position in self.current_rook_positions.items():
                    if move_from == position:
                        self.current_rook_positions[rook] = move_to

                        if '7' in move_to:
                            if rook == 'whiteRooka' or rook == 'whiteRookh':
                                self.results['WhiteSingleSwine'] = True
                            if '7' in self.current_rook_positions['whiteRooka'] and '7' in self.current_rook_positions['whiteRookh']:
                                self.results['WhiteDoubleSwine'] = True

                        if '2' in move_to:
                            if rook == 'blackRooka' or rook == 'blackRookh':
                                self.results['BlackSingleSwine'] = True
                            if '2' in self.current_rook_positions['blackRooka'] and '2' in self.current_rook_positions['blackRookh']:
                                self.results['BlackDoubleSwine'] = True

        return pd.DataFrame(self.results, index=[0])