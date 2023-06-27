import os
import pandas as pd
import chess
import matplotlib.pyplot as plt
import numpy as np

from CSVHandler import CSVHandler
from data.processing.BasicStatsGetter import BasicStatsGetter
from engines.Engine import Engine, EngineType


# HEURISTIC: "Control the center"
class CenterAnalyzer:
    def __init__(self):
        self.board = chess.Board()
        self.center_squares = [chess.E4, chess.D4,
                               chess.E5, chess.D5]
        self.fill_value = "-"
        #self.move_file = "moves_1_cleaned.csv"
        # if os.path.exists(self.move_file):
        #     self.move_dict = pd.read_csv(self.move_file, index_col=0).squeeze("columns").to_dict()
        #     # print(self.move_dict)
        # else:
        #     self.move_dict = {}
        self.engine = Engine(EngineType.STOCKFISH)
        self.limit = chess.engine.Limit(depth=20)

        return

    def evaluate_center(self, board):
        white_attack = 0
        black_attack = 0
        white_centralization = 0
        black_centralization = 0

        for square in self.center_squares:
            white_attack += self.evaluate_square_attac(square, chess.WHITE, board)
            black_attack += self.evaluate_square_attac(square, chess.BLACK, board)
            white_centralization += self.is_square_occupied_by_player(square, chess.WHITE, board)
            black_centralization += self.is_square_occupied_by_player(square, chess.BLACK, board)

        return white_attack, black_attack, white_centralization, black_centralization

    def evaluate_square_attac(self, square, perspective, board):
        """Evaluates if given square is attacked by a player, counting multiple attacks."""
        if board.is_attacked_by(perspective, square):
            attackers = board.attackers(perspective, square)
            return len(attackers)

        return 0

    def is_square_occupied_by_player(self, square, perspective, board):
        """Evaluates if a given square is occupied by a player"""
        occupying_piece = board.piece_at(square)
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
        last_move = min(len(moves), 20)

        for index in range(1, last_move):
            self.board.push_uci(moves[index])

            white_attack, black_attack, white_centralization, black_centralization = self.evaluate_center(self.board)
            result["WhiteAttack"] = result["WhiteAttack"] + "," + str(white_attack)
            result["BlackAttack"] = result["BlackAttack"] + "," + str(black_attack)
            result["WhiteCentralization"] = result["WhiteCentralization"] + "," + str(white_centralization)
            result["BlackCentralization"] = result["BlackCentralization"] + "," + str(black_centralization)

        return pd.Series(result).to_frame().T

    def analyze_results(self, result_path, output_path):
        print("Result analysis started")
        print("Loading data...")
        csv_handler = CSVHandler(result_path, output_path)
        df = csv_handler.data
        print("Manipulating data...")
        # Convert the comma-separated strings into lists of integers
        for column in ['WhiteAttack', 'BlackAttack', 'WhiteCentralization', 'BlackCentralization']:
            df[column] = df[column].apply(lambda x: list(map(int, x.split(','))))

        # Filter the DataFrame based on the 'Result' column
        white_wins = df[df['Result'] == '1-0']
        black_wins = df[df['Result'] == '0-1']
        draws = df[df['Result'] == "1/2-1/2"]

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
        # avg_white_centralization = np.array(avg_white_centralization)
        # avg_black_centralization = np.array(avg_black_centralization)
        # centralization_advantage = avg_white_centralization - avg_black_centralization
        print("Saving results...")
        # save to results file
        result = pd.DataFrame({
            'AvgWhiteCentralization': avg_white_centralization,
            'AvgBlackCentralization': avg_black_centralization,
            'AvgWhiteCentralizationWins': avg_white_centralization_wins,
            'AvgBlackCentralizationWins': avg_black_centralization_wins,
            'AvgBlackControl': avg_black_control,
            'AvgWhiteControl': avg_white_control,
            'AvgBlackControlWins': avg_black_control_wins,
            'AvgWhiteControlWins': avg_white_centralization_wins
        })
        csv_handler.save_to_csv(result)

    def analyze_results_alt(self, result_path, output_path, turns_to_analyze=100):
        print("(ALT)Result analysis started")
        print("Loading data...")
        csv_handler = CSVHandler(result_path, output_path)
        df = csv_handler.data
        print("Manipulating data...")
        # Convert the comma-separated strings into a mean of first 100 items in the list
        for column in ['WhiteAttack', 'BlackAttack', 'WhiteCentralization', 'BlackCentralization']:
            df[column] = df[column].apply(lambda x: np.mean(list(map(int, x.split(',')))[:turns_to_analyze]))

        # get and print winrates from the entire set
        bsg = BasicStatsGetter()
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df)
        # print(f"All data [W,B,D] len{len(df)}")
        print(f"{white_wr:.2%},{black_wr:.2%},{draw_rate:.2%}")

        # create a new dataframe containing only the rows that have WhiteCentralization > BlackCentralization
        df_white_advantage = df[df['WhiteCentralization'] > df['BlackCentralization']]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_advantage)
        # print(f"White advantage [W,B,D] len{len(df_white_advantage)}")
        print(f"{white_wr:.2%},{black_wr:.2%},{draw_rate:.2%}")

        # create a new dataframe containing only the rows that have WhiteCentralization < BlackCentralization
        df_black_advantage = df[df['WhiteCentralization'] < df['BlackCentralization']]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_advantage)
        # print(f"Black advantage [W,B,D] len{len(df_black_advantage)}")
        print(f"{white_wr:.2%},{black_wr:.2%},{draw_rate:.2%}")

    def plot_centralization(self, data_path):
        csv_handler = CSVHandler(data_path)
        df = csv_handler.data
        print("Manipulating data...")
        # Convert the comma-separated strings into lists of integers
        for column in ['AvgWhiteCentralization', 'AvgBlackCentralization', 'AvgWhiteCentralizationWins',
                       'BlackCentralization', 'AvgBlackCentralizationWins']:
            df[column] = df[column].apply(lambda x: list(map(int, x.split(','))))

        # print("Plotting results...")
        # color_white = '#e8fcff'
        # color_black ='#769ba8'
        # plt.figure(figsize=(12, 6))
        # plt.plot([i / 2 for i in range(len(avg_white_centralization))], avg_white_centralization, 'o',
        #          label='Centralizacja białych', color=color_white)
        # plt.plot([i / 2 for i in range(len(avg_black_centralization))], avg_black_centralization, 'o',
        #          label='Centralizacja czarnych',color=color_black)
        # # plt.plot([i / 2 for i in range(len(centralization_advantage))], centralization_advantage, 'o',
        # #          label='Przewaga centralizacji-')
        # plt.title('Średnia centralizacja a tura')
        # plt.xlabel('tura')
        # plt.ylabel('średnia centralizacja')
        # plt.legend()
        # plt.show()
        #
        # plt.figure(figsize=(12, 6))
        # plt.plot([i / 2 for i in range(len(avg_white_control))], avg_white_control, 'o', label='Kontrola białych')
        # plt.plot([i / 2 for i in range(len(avg_black_control))], avg_black_control, 'o', label='Kontrola czarnych')
        # plt.plot([i / 2 for i in range(len(avg_white_control_wins))], avg_white_control_wins, 'o',
        #          label='Kontrola białych (wygrane)')
        # plt.plot([i / 2 for i in range(len(avg_black_control_wins))], avg_black_control_wins, 'o',
        #          label='Kontrola czarnych (wygrane)')
        # plt.title('Średnia kontrola centrum a tura')
        # plt.xlabel('tura')
        # plt.ylabel('średnia kontrola centrum')
        # plt.legend()
        # plt.show()

    def analyze_game_empirical_stockfish(self, data):
        self.board.reset()
        moves = eval(data['Moves'])
        white_attack_incr_arr = eval(data["WhiteAttackIncrease"])
        black_attack_incr_arr = eval(data["BlackAttackIncrease"])
        white_centr_incr_arr = eval(data["WhiteCentralizationIncrease"])
        black_centr_incr_arr = eval(data["BlackCentralizationIncrease"])
        #convert to strings
        white_attack_incr_arr = [str(x) for x in white_attack_incr_arr]
        black_attack_incr_arr = [str(x) for x in black_attack_incr_arr]
        white_centr_incr_arr = [str(x) for x in white_centr_incr_arr]
        black_centr_incr_arr = [str(x) for x in black_centr_incr_arr]



        max_move = min(len(moves), 20)

        for i in range(0, max_move):
            curr_eval = white_attack_incr_arr[i]
            curr_move = moves[i]

            if curr_eval != "-1":
                self.board.push_uci(curr_move)
                continue

            #print("-1 found!")
            hypothetical_board = self.board.copy()
            white_attack_before, black_attack_before, white_centralization_before, black_centralization_before = self.evaluate_center(
                hypothetical_board)
            best_move = self.engine.get_best_move(hypothetical_board, self.limit)
            hypothetical_board.push_uci(best_move)
            white_attack_after, black_attack_after, white_centralization_after, black_centralization_after = self.evaluate_center(
                hypothetical_board)
            white_attack_incr = "1" if (white_attack_after > white_attack_before) else "0"
            black_attack_incr = "1" if (black_attack_after > black_attack_before) else "0"
            white_centralization_incr = "1" if (white_centralization_after > white_centralization_before) else "0"
            black_centraliztion_incr = "1" if (black_centralization_after > black_centralization_before) else "0"

            white_attack_incr_arr[i] = white_attack_incr
            black_attack_incr_arr[i] = black_attack_incr
            white_centr_incr_arr[i] = white_centralization_incr
            black_centr_incr_arr[i] = black_centraliztion_incr
            self.board.push_uci(curr_move)

        # convert to comma separeted lists
        white_attack_incr_arr = ','.join(list(white_attack_incr_arr))
        black_attack_incr_arr = ','.join(list(black_attack_incr_arr))
        white_centr_incr_arr = ','.join(list(white_centr_incr_arr))
        black_centr_incr_arr = ','.join(list(black_centr_incr_arr))


        result = {
            "WhiteAttackIncrease": white_attack_incr_arr,
            "BlackAttackIncrease": black_attack_incr_arr,
            "WhiteCentralizationIncrease": white_centr_incr_arr,
            "BlackCentralizationIncrease": black_centr_incr_arr
        }

        return pd.Series(result).to_frame().T


    def analyze_game_empirical(self, moves):
        self.board.reset()

        white_attack_before, black_attack_before, white_centralization_before, black_centralization_before = self.evaluate_center(
            self.board)
        best_move = self.get_best_move_from_dict(self.board)

        if best_move:
            hypothetical_board = self.board.copy()
            hypothetical_board.push_uci(best_move)
            white_attack_after, black_attack_after, white_centralization_after, black_centralization_after = self.evaluate_center(
                hypothetical_board)
            white_attack_incr = "1" if (white_attack_after > white_attack_before) else "0"
            black_attack_incr = "1" if (black_attack_after > black_attack_before) else "0"
            white_centralization_incr = "1" if (white_centralization_after > white_centralization_before) else "0"
            black_centraliztion_incr = "1" if (black_centralization_after > black_centralization_before) else "0"
            # print(f"{white_attack_incr},{black_attack_incr},{white_centralization_incr},{black_centraliztion_incr}")
            result = {
                "WhiteAttackIncrease": white_attack_incr,
                "BlackAttackIncrease": black_attack_incr,
                "WhiteCentralizationIncrease": white_centralization_incr,
                "BlackCentralizationIncrease": black_centraliztion_incr,
            }
        else:
            result = {
                "WhiteAttackIncrease": "-1",
                "BlackAttackIncrease": "-1",
                "WhiteCentralizationIncrease": "-1",
                "BlackCentralizationIncrease": "-1"
            }

        self.board.push_uci(moves[0])

        # assign after values to before vars
        # white_attack_before, black_attack_before, white_centralization_before, black_centralization_before = white_attack_after, black_attack_after, white_centralization_after, black_centralization_after
        max_move = min(len(moves), 20)
        for i in range(1, max_move):
            curr_move = moves[i]
            best_move = self.get_best_move_from_dict(self.board)

            if best_move is not None:
                # print("i'm here")
                hypothetical_board = self.board.copy()
                white_attack_before, black_attack_before, white_centralization_before, black_centralization_before = self.evaluate_center(
                    hypothetical_board)
                hypothetical_board.push_uci(best_move)
                white_attack_after, black_attack_after, white_centralization_after, black_centralization_after = self.evaluate_center(
                    hypothetical_board)

                white_attack_incr = "1" if (white_attack_after > white_attack_before) else "0"
                black_attack_incr = "1" if (black_attack_after > black_attack_before) else "0"
                white_centralization_incr = "1" if (white_centralization_after > white_centralization_before) else "0"
                black_centraliztion_incr = "1" if (black_centralization_after > black_centralization_before) else "0"

                result["WhiteAttackIncrease"] = result[
                                                    "WhiteAttackIncrease"] + "," + white_attack_incr
                result["BlackAttackIncrease"] = result[
                                                    "BlackAttackIncrease"] + "," + black_attack_incr
                result["WhiteCentralizationIncrease"] = result[
                                                            "WhiteCentralizationIncrease"] + "," + white_centralization_incr
                result["BlackCentralizationIncrease"] = result[
                                                            "BlackCentralizationIncrease"] + "," + black_centraliztion_incr
            else:
                result["WhiteAttackIncrease"] = result["WhiteAttackIncrease"] + ",-1"
                result["BlackAttackIncrease"] = result["BlackAttackIncrease"] + ",-1"
                result["WhiteCentralizationIncrease"] = result["WhiteCentralizationIncrease"] + ",-1"
                result["BlackCentralizationIncrease"] = result["BlackCentralizationIncrease"] + ",-1"
                # print('olo')

            self.board.push_uci(curr_move)

        return pd.Series(result).to_frame().T


    def get_best_move_from_dict(self, board):
        board_fen = board.fen()

        if board_fen in self.move_dict:
            # res = self.move_dict[board_fen]
            # print(f"FOUND A MOVE {res}")
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
