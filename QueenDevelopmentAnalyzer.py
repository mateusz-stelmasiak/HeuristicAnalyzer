import chess
import pandas as pd
from collections import namedtuple
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import numpy as np


# HEURISTIC: "Don't develop the queen early in the game"
class QueenDevelopmentAnalyzer:
    def __init__(self, data_path, early_move_threshold=10):
        self.df = self.__clean_data(data_path)
        self.output_file = data_path[:len(data_path) - 4] + "_queen_development.csv"
        self.early_move_threshold = early_move_threshold

    def analyze_queen_development(self, data_file_path=False):
        early_queen_games_white, not_early_queen_games_white, early_queen_games_black, not_early_queen_games_black = self.get_queen_development_vars_from_data(
            data_file_path)

        early_queen_metrics_white = self.__calculate_performance_metrics(early_queen_games_white, chess.WHITE)
        not_early_queen_metrics_white = self.__calculate_performance_metrics(not_early_queen_games_white, chess.WHITE)
        early_queen_metrics_black = self.__calculate_performance_metrics(early_queen_games_black, chess.BLACK)
        not_early_queen_metrics_black = self.__calculate_performance_metrics(not_early_queen_games_black, chess.BLACK)

        # win_ratios_ttest_white = ttest_ind(early_queen_games_white['result'], not_early_queen_games_white['result'],
        #                                    equal_var=False)
        # win_ratios_ttest_black = ttest_ind(early_queen_games_black['result'], not_early_queen_games_black['result'],
        #                                    equal_var=False)

        self.plot_win_ratios(early_queen_metrics_white, not_early_queen_metrics_white, early_queen_metrics_black,
                             not_early_queen_metrics_black)
        # return early_queen_metrics_white, not_early_queen_metrics_white, win_ratios_ttest_white, early_queen_metrics_black, not_early_queen_metrics_black, win_ratios_ttest_black

    def plot_win_ratios(self, early_queen_metrics_white, not_early_queen_metrics_white, early_queen_metrics_black,
                        not_early_queen_metrics_black):
        labels = ['Early Queen Move', 'No Early Queen Move']
        white_win_ratios = [early_queen_metrics_white.win_ratio, not_early_queen_metrics_white.win_ratio]
        black_win_ratios = [early_queen_metrics_black.win_ratio, not_early_queen_metrics_black.win_ratio]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, white_win_ratios, width, label='White')
        rects2 = ax.bar(x + width / 2, black_win_ratios, width, label='Black')

        ax.set_ylabel('Win Ratios')
        ax.set_title('Win Ratios by Early Queen Move and Player Color')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        plt.show()

    def analyze_queen_movement(self):
        for index, row in self.df.iterrows():
            print(f"[{index + 1}/{len(self.df.index)}] Analysing queen's movement...")

            early_queen_move_white, early_queen_move_black = self.get_early_queen_moves(eval(row['moves']))
            self.df.at[index, f"early_queen_move_white"] = early_queen_move_white
            self.df.at[index, f"early_queen_move_black"] = early_queen_move_black

        self.df.to_csv(self.output_file, index=False)

    def get_early_queen_moves(self, move_list):
        board = chess.Board()
        early_queen_move_white = 0
        early_queen_move_black = 0

        for move in move_list:
            # Break the loop if we analyzed enough early moves
            if board.fullmove_number >= self.early_move_threshold:
                break

            # Parse the move and check if it's legal
            move_obj = chess.Move.from_uci(move)
            if not board.is_legal(move_obj):
                break

            # Check if the move is a queen move
            piece_to_move = board.piece_at(move_obj.from_square)
            if piece_to_move.piece_type != chess.QUEEN:
                board.push(move_obj)
                continue

            # Check if the move hides the queen or doesn't develop its position
            if self.is_non_developing_queen_move(board, move_obj):
                board.push(move_obj)
                continue

            # All checks failed, it must be a developing queen move
            if board.turn == chess.WHITE:
                early_queen_move_white = board.fullmove_number
            else:
                early_queen_move_black = board.fullmove_number

            # Check if we can't break the loop early
            if early_queen_move_white !=0 and early_queen_move_black != 0:
                break

            board.push(move_obj)

        return early_queen_move_white, early_queen_move_black

    def is_non_developing_queen_move(self, board, move):
        """Determines if a given move hides the queen or doesn't develop its position."""
        attacked_before = board.is_attacked_by(not board.turn, move.from_square)
        mobility_before = self.__get_queen_mobility(board, move.from_square)

        # Check if the queen moves closer to or further away from the player's base
        # rank_diff = chess.square_rank(move.to_square) - chess.square_rank(move.from_square)
        # moving_closer_to_base = (rank_diff < 0) if board.turn == chess.WHITE else (rank_diff > 0)
        # if moving_closer_to_base:
        #     return True

        # Make the move and check if the queen is attacked after the move
        board.push(move)
        attacked_after = board.is_attacked_by(board.turn, move.to_square)
        mobility_after = self.__get_queen_mobility(board, move.to_square, True)
        # print(board)
        # Undo the move
        board.pop()

        # Determine if the move is hiding or non-developing
        is_capture = board.is_capture(move)
        was_escaping = attacked_before and not attacked_after and not is_capture
        new_position_weaker = mobility_before >= 1.2 * mobility_after

        if was_escaping or new_position_weaker:
            return True

        return False

    def __get_queen_mobility(self, board, queen_square, flip=False):
        """Calculates the queen's mobility (number of legal moves) on the given board."""
        queen_moves = []

        # Push a null move to switch the turn
        if flip: board.push(chess.Move.null())

        for move in board.legal_moves:
            if move.from_square == queen_square:
                queen_moves.append(move)

        # Pop the null move to restore the original board state
        if flip: board.pop()

        return len(queen_moves)

    def get_queen_development_vars_from_data(self, data_file_path=False):
        """Categorizes games based on early queen moves for both white and black perspectives."""
        if not data_file_path:
            self.analyze_queen_movement()
        else:
            self.df = self.__clean_data(str(data_file_path))

        # Filter and segment the data
        early_queen_games_white = self.df[self.df['early_queen_move_white'] > 0]
        not_early_queen_games_white = self.df[self.df['early_queen_move_white'] == 0.0]
        early_queen_games_black = self.df[self.df['early_queen_move_black'] > 0]
        not_early_queen_games_black = self.df[self.df['early_queen_move_black'] == 0.0]

        return early_queen_games_white, not_early_queen_games_white, early_queen_games_black, not_early_queen_games_black

    def __calculate_performance_metrics(self, df, perspective):
        """Calculates performance metrics for a given dataframe."""
        total_games = len(df)
        if perspective == chess.BLACK:
            wins = len(df[df['result'] == '0-1'])
        else:
            wins = len(df[df['result'] == '1-0'])
        draws = len(df[df['result'] == '1/2-1/2'])
        win_ratio = wins / total_games
        draw_ratio = draws / total_games
        avg_game_length = df['no_of_moves'].mean()
        return namedtuple('PerformanceMetrics', ['win_ratio', 'draw_ratio', 'avg_game_length'])(win_ratio, draw_ratio,
                                                                                                avg_game_length)

    def __clean_data(self, file_path):
        """Loads and cleans the input data."""
        df = pd.read_csv(file_path)
        df = df.dropna()  # Remove rows with missing values
        # df = df[(df['player_white'] >= self.min_elo_rating) & (df['player_black'] >= self.min_elo_rating)]  # Filter by Elo rating
        return df
