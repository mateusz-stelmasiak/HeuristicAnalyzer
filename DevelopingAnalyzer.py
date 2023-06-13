import os

import chess
import pandas as pd

from CSVHandler import CSVHandler


# Heuristic develop pieces before pawns

class DevelopingAnalyzer(CSVHandler):

    def __init__(self, limit):
        self.board = chess.Board()
        self.limit = limit

    def analyze_game(self, moves):
        columns = ['test']
        results = [1]

        return pd.DataFrame(results, columns=columns)

