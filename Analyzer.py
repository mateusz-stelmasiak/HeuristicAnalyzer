import concurrent
import itertools
import os

import chess
import pandas as pd
from tqdm import tqdm

import CSVHandler
from CenterAnalyzer import CenterAnalyzer
from DevelopingAnalyzer import DevelopingAnalyzer
from CastlingAnalyzer import CastlingAnalyzer
from SwineAnalyzer import SwineAnalyzer
from engines.Engine import EngineType, Engine
from concurrent.futures import ProcessPoolExecutor


class Analyzer:
    def __init__(self, data_path, output_path, amount_to_analise=None, amount_of_workers=1):
        self.data_path = data_path
        self.dataReader = CSVHandler.CSVHandler(data_path, output_path)
        self.data = self.dataReader.data

        self.amount_of_workers = amount_of_workers
        self.sf_depth_limit = 20

        self.amount_to_analise = amount_to_analise
        if not amount_to_analise:
            self.amount_to_analise = len(self.data)

    def print_data(self):
        print(self.dataReader.data)

    @staticmethod
    def print_as_pgn(moves):
        game = chess.pgn.Game()
        moves_arr = []
        for move in moves:
            move_obj = chess.Move.from_uci(move)
            moves_arr.append(move_obj)

        game.add_line(moves_arr)
        print(game.mainline())

    @staticmethod
    def analyze_game(index, row, sf_depth_limit):
        #castling_analyzer = CastlingAnalyzer(sf_depth_limit)
        #development_analyzer = DevelopingAnalyzer(sf_depth_limit)
        # swine_analyzer = SwineAnalyzer(sf_depth_limit)
        center_analyzer = CenterAnalyzer()
        moves = eval(row['Moves'])
        result_data = pd.DataFrame({"Id": index,
                                    'WhiteElo': [row['WhiteElo']],
                                    'BlackElo': [row['BlackElo']],
                                    'Result': [row['Result']]})

        # CASTLING ANALYZER
        # result_data = pd.concat([result_data, castling_analyzer.analyze_game(moves)], axis=1)
        # DEVELOPMENT ANALYZER
        #result_data = pd.concat([result_data, development_analyzer.analyze_game(moves)], axis=1)
        #Center analyzer
        result_data = pd.concat([result_data, center_analyzer.analyze_game_empirical(moves)], axis=1)
        # SWINE ANALYZER
        # result_data = pd.concat([result_data, swine_analyzer.analyze_game(moves)], axis=1)
        return result_data

    def run_analysis(self, save_interval=50,skip_first=0):
        results = []
        self.dataReader.delete_output_file()

        try:
            with ProcessPoolExecutor(max_workers=self.amount_of_workers) as executor:
                game_iterator = iter(self.data.iterrows())
                [next(game_iterator) for _ in range(skip_first)]
                futures = {executor.submit(Analyzer.analyze_game, index, row, self.sf_depth_limit) for index, row in
                           itertools.islice(game_iterator, self.amount_to_analise)}
                completed_games = 0

                for future in concurrent.futures.as_completed(futures):
                    try:
                        result_data = future.result()
                    except Exception as exc:
                        print(f'Game generated an exception: {exc}')
                    else:
                        results.append(result_data)
                        completed_games += 1
                        if completed_games % save_interval == 0:
                            df = pd.concat(results, axis=0)
                            self.dataReader.append_to_csv(df)
                            results = []
                    print(f"Completed {completed_games}/{self.amount_to_analise-skip_first} games")

        except KeyboardInterrupt:
            print("Saving data and closing the program...")
            df = pd.concat(results, axis=0)
            self.dataReader.append_to_csv(df)
            raise SystemExit

        # save games that were left in the buffer
        if len(results) != 0:
            df = pd.concat(results, axis=0)
            self.dataReader.append_to_csv(df)

        return
