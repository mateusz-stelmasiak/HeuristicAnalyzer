import chess
import pandas as pd
from tqdm import tqdm

import CSVHandler
from DevelopingAnalyzer import DevelopingAnalyzer
from CastlingAnalyzer import CastlingAnalyzer
from SwineAnalyzer import SwineAnalyzer
from engines.Engine import EngineType, Engine


class Analyzer:
    def __init__(self, data_path, output_path, amount_to_analise=None):
        self.data_path = data_path
        self.board = chess.Board()
        self.engine = Engine(EngineType.STOCKFISH)
        self.limit = chess.engine.Limit(depth=21)
        self.dataReader = CSVHandler.CSVHandler(data_path, output_path)
        self.data = self.dataReader.data
        self.developing_analyzer = DevelopingAnalyzer()
        self.castling_analyzer = CastlingAnalyzer(self.engine, self.limit)
        self.swine_analyzer = SwineAnalyzer(self.engine, self.limit)
        self.amount_to_analise = amount_to_analise
        if not amount_to_analise:
            self.amount_to_analise = len(self.data)

    def print_data(self):
        print(self.dataReader.data)

    def print_as_pgn(self, moves):
        game = chess.pgn.Game()
        moves_arr = []
        for move in moves:
            move_obj = chess.Move.from_uci(move)
            moves_arr.append(move_obj)

        game.add_line(moves_arr)
        print(game.mainline())

    def run_analysis(self, save_interval=1000):
        results = []
        self.dataReader.delete_output_file()

        try:
            for index, row in tqdm(self.data.iterrows(), total=self.amount_to_analise, desc="Analyzing games"):

                if index != 0 and index % save_interval == 0:
                    df = pd.concat(results, axis=0)
                    self.dataReader.append_to_csv(df)
                    results = []

                if index >= self.amount_to_analise:
                    break

                moves = eval(row['Moves'])
                result_data = pd.DataFrame({'WhiteElo': [row['WhiteElo']],
                                            'BlackElo': [row['BlackElo']],
                                            'Result': [row['Result']]})

                # CASTLING ANALYZER
                result_data = pd.concat([result_data, self.castling_analyzer.analyze_game(moves)], axis=1)
                # DEVELOPMENT ANALYZER
                # result_data = pd.concat([result_data, self.developing_analyzer.analyze_game(moves)], axis=1)
                # SWINE ANALYZER
                # result_data = pd.concat([result_data, self.swine_analyzer.analyze_game(moves)], axis=1)

                results.append(result_data)
        except KeyboardInterrupt:
            print(f"Finished analysis at {index}")
            print("Saving data and closing the program...")
            df = pd.concat(results, axis=0)
            self.dataReader.append_to_csv(df)
            raise SystemExit

        df = pd.concat(results, axis=0)
        self.dataReader.append_to_csv(df)
