import chess
import pandas as pd
from tqdm import tqdm

import CSVHandler
from DevelopingAnalyzer import DevelopingAnalyzer
from CastlingAnalyzer import CastlingAnalyzer
from engines.Engine import EngineType, Engine


class Analyzer:
    def __init__(self, data_path, output_path, amount_to_analise=None):
        self.data_path = data_path
        self.board = chess.Board()
        self.engine = Engine(EngineType.STOCKFISH)
        self.limit = chess.engine.Limit(depth=15)
        self.dataReader = CSVHandler.CSVHandler(data_path, output_path)
        self.data = self.dataReader.data
        self.developing_analyzer = DevelopingAnalyzer()
        self.castling_analyzer = CastlingAnalyzer()
        self.amount_to_analise = amount_to_analise
        if not amount_to_analise:
            self.amount_to_analise = len(self.data)

    def print_data(self):
        print(self.dataReader.data)

    def run_analysis(self):

        for index, row in tqdm(self.data.iterrows(), total=self.amount_to_analise, desc="Analyzing games"):

            if index >= self.amount_to_analise:
                break

            moves = eval(row['Moves'])
            result_data = pd.DataFrame({'WhiteElo': [row['WhiteElo']],
                                        'BlackElo': [row['BlackElo']],
                                        'Result': [row['Result']]})

            castling_analyzer_results = self.castling_analyzer.analytical_method(moves)
            result_data = pd.concat([result_data, castling_analyzer_results], axis=1)

            analyzer_results = self.developing_analyzer.analyze_game(moves)

            if analyzer_results is not None:
                result_data = pd.concat([result_data, analyzer_results], axis=1)

            self.dataReader.append_to_csv(result_data)

    def run_castling_analyzer(self, board):
        return
        # HEURISTIC: Castle soon
        # castling_analyzer = CastlingAnalyzer.CastlingAnalyzer(data_file_path)
        # castling_analyzer.calculate_castling_turns()
        # castling_analyzer.calculate_win_rates()
        # castling_analyzer.calculate_castling_effectiveness()
        # castling_analyzer.analyse_castling_data()
