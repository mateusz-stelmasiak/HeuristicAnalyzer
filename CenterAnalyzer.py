import os
import pandas as pd
import chess
import matplotlib.pyplot as plt
import numpy as np

from CSVHandler import CSVHandler


# HEURISTIC: "Control the center"
class CenterAnalyzer:
    def __init__(self):
        self.board = chess.Board()
        self.center_squares = [chess.E4, chess.D4,
                               chess.E5, chess.D5]
        self.fill_value = "-"
        self.move_file = "subeliteMoves_cleaned.csv"
        if os.path.exists(self.move_file):
            self.move_dict = pd.read_csv(self.move_file, index_col=0).squeeze("columns").to_dict()
        else:
            self.move_dict = {}

        return

    def evaluate_center(self):
        white_attack = 0
        black_attack = 0
        white_centralization = 0
        black_centralization = 0

        for square in self.center_squares:
            white_attack += self.evaluate_square_attac(square, chess.WHITE)
            black_attack += self.evaluate_square_attac(square, chess.BLACK)
            white_centralization += self.is_square_occupied_by_player(square, chess.WHITE)
            black_centralization += self.is_square_occupied_by_player(square, chess.BLACK)

        return white_attack, black_attack, white_centralization, black_centralization

    def evaluate_square_attac(self, square, perspective):
        """Evaluates if given square is attacked by a player, counting multiple attacks."""
        if self.board.is_attacked_by(perspective, square):
            attackers = self.board.attackers(perspective, square)
            return len(attackers)

        return 0

    def is_square_occupied_by_player(self, square, perspective):
        """Evaluates if a given square is occupied by a player"""
        occupying_piece = self.board.piece_at(square)
        if occupying_piece and occupying_piece.color == perspective:
            return 1

        return 0

    def analyze_game(self, moves):
        # set up the board and evaluate first postion (always the same)
        self.board.reset()
        self.board.push_uci(moves[0])
        white_attack, black_attack, white_centralization, black_centralization = self.evaluate_center()
        result = {
            "WhiteAttack": str(white_attack),
            "BlackAttack": str(black_attack),
            "WhiteCentralization": str(white_centralization),
            "BlackCentralization": str(black_centralization)
        }

        for index in range(1, len(moves)):
            self.board.push_uci(moves[index])

            white_attack, black_attack, white_centralization, black_centralization = self.evaluate_center()
            result["WhiteAttack"] = result["WhiteAttack"] + "," + str(white_attack)
            result["BlackAttack"] = result["BlackAttack"] + "," + str(black_attack)
            result["WhiteCentralization"] = result["WhiteCentralization"] + "," + str(white_centralization)
            result["BlackCentralization"] = result["BlackCentralization"] + "," + str(black_centralization)

        return pd.Series(result).to_frame().T

    def analyze_results(self, result_path):
        csv = CSVHandler(result_path)
        df = csv.data

        # Convert the comma-separated strings into lists of integers
        for column in ['WhiteAttack', 'BlackAttack', 'WhiteCentralization', 'BlackCentralization']:
            df[column] = df[column].apply(lambda x: list(map(int, x.split(','))))

        # Filter the DataFrame based on the 'Result' column
        white_wins = df[df['Result'] == '1-0']
        black_wins = df[df['Result'] == '0-1']

        # Calculate the average centralization and control for each half-turn
        avg_white_centralization = []
        avg_black_centralization = []
        avg_white_centralization_wins = []
        avg_black_centralization_wins = []
        avg_white_control = []
        avg_black_control = []
        avg_white_control_wins = []
        avg_black_control_wins = []
        max_half_turns = max(white_wins['WhiteAttack'].apply(len).max(),
                             black_wins['BlackAttack'].apply(len).max())

        for i in range(max_half_turns):
            avg_white_centralization.append(
                df['WhiteCentralization'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())
            avg_black_centralization.append(
                df['BlackCentralization'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())
            avg_black_centralization_wins.append(
                black_wins['BlackCentralization'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())
            avg_white_centralization_wins.append(
                white_wins['WhiteCentralization'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())

            avg_white_control.append(df['WhiteAttack'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())
            avg_black_control.append(df['BlackAttack'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())
            avg_white_control_wins.append(
                white_wins['WhiteAttack'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())
            avg_black_control_wins.append(
                black_wins['BlackAttack'].apply(lambda x: x[i] if i < len(x) else np.nan).mean())

        avg_white_centralization = np.array(avg_white_centralization)
        avg_black_centralization = np.array(avg_black_centralization)

        # Calculate the centralization advantage
        centralization_advantage = avg_white_centralization - avg_black_centralization

        plt.figure(figsize=(12, 6))
        plt.plot([i / 2 for i in range(len(avg_white_centralization))], avg_white_centralization, 'o',
                 label='Centralizacja białych')
        plt.plot([i / 2 for i in range(len(avg_black_centralization))], avg_black_centralization, 'o',
                 label='Centralizacja czarnych')
        plt.plot([i / 2 for i in range(len(centralization_advantage))], centralization_advantage, 'o',
                 label='Przewaga centralizacji-')
        plt.title('Średnia centralizacja a tura')
        plt.xlabel('tura')
        plt.ylabel('średnia centralizacja')
        plt.legend()
        plt.show()

        plt.figure(figsize=(12, 6))
        plt.plot([i / 2 for i in range(len(avg_white_control))], avg_white_control, 'o', label='Kontrola białych')
        plt.plot([i / 2 for i in range(len(avg_black_control))], avg_black_control, 'o', label='Kontrola czarnych')
        plt.plot([i / 2 for i in range(len(avg_white_control_wins))], avg_white_control_wins, 'o',
                 label='Kontrola białych (wygrane)')
        plt.plot([i / 2 for i in range(len(avg_black_control_wins))], avg_black_control_wins, 'o',
                 label='Kontrola czarnych (wygrane)')
        plt.title('Średnia kontrola centrum a tura')
        plt.xlabel('tura')
        plt.ylabel('średnia kontrola centrum')
        plt.legend()
        plt.show()

    def analyze_game_empirical(self, moves):
        self.board.reset()

        for move in moves:
            best_move = self.get_best_move_from_dict(self.board)
            if best_move:
                white_attack_before, black_attack_before, white_centralization_before, black_centralization_before = self.evaluate_center()
                self.board.push_uci(best_move.uci())
                white_attack_after, black_attack_after, white_centralization_after, black_centralization_after = self.evaluate_center()

                # result["WhiteAttack"] = result["WhiteAttack"] + "," + str(white_attack)
                # result["BlackAttack"] = result["BlackAttack"] + "," + str(black_attack)
                # result["WhiteCentralization"] = result["WhiteCentralization"] + "," + str(white_centralization)
                # result["BlackCentralization"] = result["BlackCentralization"] + "," + str(black_centralization)
                result_dict = {
                    "WhiteAttackIncrease": white_attack_after > white_attack_before,
                    "BlackAttackIncrease": black_attack_after > black_attack_before,
                    "WhiteCentralizationIncrease": white_centralization_after > white_centralization_before,
                    "BlackCentralizationIncrease": black_centralization_after > black_centralization_before,
                }
                return pd.DataFrame(result_dict, index=[0])
            result_dict = {
                "WhiteAttackIncrease": -1,
                "BlackAttackIncrease": -1,
                "WhiteCentralizationIncrease": -1,
                "BlackCentralizationIncrease": -1,
            }
            return pd.DataFrame(result_dict, index=[0])

    def get_best_move_from_dict(self, board):
        board_fen = board.fen()

        if board_fen in self.move_dict:
            return self.move_dict[board_fen]

        return None

        # print('Correlation between average centralization and winning probability:')
        # print('White:', np.corrcoef(avg_white_centralization[white_wins], white_wins.sum())[0, 1])
        # print('Black:', np.corrcoef(avg_black_centralization[black_wins], black_wins.sum())[0, 1])

# def create_plot(self):
#        data = pd.read_csv(self.output_file)
#        white_avg_center_control = []
#        black_avg_center_control = []
#
#        for index, row in data.iterrows():
#            print(f"[{index + 1}/{len(data.index)}]Analysing...")
#
#            center_control_list = eval(row["center_control"])
#            game_turns = len(center_control_list)
#
#            for i, control_tuple in enumerate(center_control_list):
#                if i >= len(white_avg_center_control):
#                    white_avg_center_control.append(0)
#                    black_avg_center_control.append(0)
#
#                if len(control_tuple) == 5:
#                    _, _, _, white_control, black_control = control_tuple
#                    black_avg_center_control[i] += black_control / game_turns
#                elif len(control_tuple) == 3:
#                    _, _, white_control = control_tuple
#                else:
#                    continue
#
#                white_avg_center_control[i] += white_control / game_turns
#
#        turns = len(white_avg_center_control)
#        white_avg_center_control = [control / turns for control in white_avg_center_control]
#        black_avg_center_control = [-control / turns for control in black_avg_center_control]
#
#        plt.plot(white_avg_center_control, label="White", color='blue')
#        plt.plot(black_avg_center_control, label="Black", color='black')
#        plt.xlabel("Turns")
#        plt.ylabel("Avg Center Control")
#        plt.axhline(0, color='grey', linestyle="dashed")
#        plt.xlim(right=150)
#        plt.legend(loc="upper right")
#        plt.title("Average Center control by Turns")
#
#        plt.show()
