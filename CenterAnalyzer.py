import os
import pandas as pd
import chess
import matplotlib.pyplot as plt


# HEURISTIC: "Control the center"
class CenterAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.board = chess.Board()
        self.center_squares = [chess.E4, chess.D4,
                               chess.E5, chess.D5]
        return


    def evaluate_center(self, board, perspective):
        """Evaluates the number of center squares attacked by a player, counting multiple attacks."""
        center_control = 0

        for square in self.center_squares:
            if board.is_attacked_by(perspective, square):
                attackers = board.attackers(perspective, square)
                center_control += len(attackers)

        return center_control

    # Looks through each game, moving average of % coverage of center
    def analyze_center(self):
        data = self.__load_data()
        data["center_control"] = "-"
        buffer = []

        for index, row in data.iterrows():
            print(f"Analysing row {index + 1}/{len(data.index)}")
            result = []
            self.board = chess.Board()
            moves = eval(row['moves'])

            for move_string in moves:
                move_obj = chess.Move.from_uci(move_string)

                if not self.board.is_legal(move_obj):
                    print(f"Illegal move in game at row {index}")
                    break

                black_control = self.evaluate_center(self.board, chess.BLACK)
                white_control = self.evaluate_center(self.board, chess.WHITE)
                res_control = (white_control - black_control)

                item = {res_control, white_control, black_control}
                result.append(item)
                buffer.append(item)
                self.board.push(move_obj)

            if index % self.buffer_size == 0:
                self.__save_to_csv(buffer, "partial_outputs.csv")
                buffer = []

            data.at[index, f"center_control"] = str(result)

        self.__save_to_csv(data, self.output_file)
        return data



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

