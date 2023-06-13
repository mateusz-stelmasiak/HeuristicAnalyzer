import os

import chess
import pandas as pd

from DataReader import DataReader


# Heuristic develop pieces before pawns

class DevelopingAnalyzer(DataReader):

    def __init__(self, limit):
        self.board = chess.Board()
        self.limit = limit

    def analyze_game(self, moves):
        columns = ['test']
        results = [1]

        return pd.DataFrame(results, columns=columns)

