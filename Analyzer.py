import chess
import pandas as pd

import CSVHandler
import DevelopingAnalyzer
from CastlingAnalyzer import CastlingAnalyzer
from engines.Engine import EngineType, Engine


class Analyzer:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.board = chess.Board()
        self.engine = Engine(EngineType.STOCKFISH)
        self.limit = chess.engine.Limit(depth=15)
        self.dataReader = CSVHandler.CSVHandler(data_path, output_path)
        self.data = self.dataReader.data
        self.developing_analyzer = DevelopingAnalyzer.DevelopingAnalyzer(self.limit)

    def print_data(self):
        print(self.dataReader.data)

    def run_analysis(self):
        result_file = "results.csv"
        result_data = []
        for index, row in self.data.iterrows():
            print(f"Analyzing game {index + 1}/{len(self.data.index)}")
            moves = eval(row['Moves'])
            white_elo = row['WhiteElo']
            black_elo = row['BlackElo']
            result = row['Result']

            analyzer_results = self.developing_analyzer.analyze_game(moves)  # lala

            if analyzer_results is not None:
                result_data.append([white_elo, black_elo, result] + analyzer_results.values.tolist())
            else:
                result_data.append([white_elo, black_elo, result])

            if analyzer_results is not None:
                columns = ['WhiteElo', 'BlackElo', 'Result'] + analyzer_results.columns.tolist()
            else:
                columns = ['WhiteElo', 'BlackElo', 'Result']

            result_df = pd.DataFrame(result_data, columns=columns)

            result_df.to_csv(result_file, index=False)

            self.dataReader.append_to_csv(result_df)

    def run_castling_analyzer(self, board):
        return
        # HEURISTIC: Castle soon
        # castling_analyzer = CastlingAnalyzer.CastlingAnalyzer(data_file_path)
        # castling_analyzer.calculate_castling_turns()
        # castling_analyzer.calculate_win_rates()
        # castling_analyzer.calculate_castling_effectiveness()
        # castling_analyzer.analyse_castling_data()
