import os
import chess
import pandas as pd
from engines.Engine import EngineType, Engine
import matplotlib.pyplot as plt


# HEURISTIC: "Castle soon (to protect your king and develop your rook)"
class CastlingAnalyzer:

    def __init__(self):
        self.early_turn_cutoff_index = 15 * 2
        # start the search from 5th turn (10 element of the array) as the players cannot castle earlier
        self.earliest_castling_turn_index = 5 * 2
        self.fill_value = "-"  # value that is put if player didn't castle at all
        self.castling_moves = {
            "white_short_castle": "e4g4",
            "white_long_castle": "e4c4",
            "black_short_castle": "e8g8",
            "black_long_castle": "e8c8"
        }

    def analytical_method(self, moves):
        print(f"Looking for castling in {moves}")
        
        result = {
            "WhiteShortCastle": self.fill_value,
            "WhiteLongCastle": self.fill_value,
            "BlackShortCastle": self.fill_value,
            "BlackLongCastle": self.fill_value
        }
        white_castled_flag = False
        black_castled_flag = False

        # start the search from 5th turn
        for turn_index in range(self.earliest_castling_turn_index, self.early_turn_cutoff_index):
            curr_move = moves[turn_index]
            print(f"Looking at {curr_move} (index {turn_index})")

            if white_castled_flag and black_castled_flag:
                break

            # check for white castle
            if not white_castled_flag:
                if curr_move == self.castling_moves['white_short_castle']:
                    result['WhiteShortCastle'] = turn_index//2+1
                    white_castled_flag = True
                    continue

                if curr_move == self.castling_moves['white_long_castle']:
                    result['WhiteLongCastle'] = turn_index//2+1
                    white_castled_flag = True
                    continue

            if not black_castled_flag:
                if curr_move == self.castling_moves['black_short_castle']:
                    result['BlackShortCastle'] = turn_index//2+1
                    black_castled_flag = True
                    continue

                if curr_move == self.castling_moves['black_long_castle']:
                    result['BlackLongCastle'] = turn_index//2+1
                    black_castled_flag = True
                    continue

        return pd.DataFrame(result)

    # we find games in the database that have the possibility of castling early,
    # and then evaluate those with the stockfish engine and see the proportion
    # in which castling is the best move.
    def calculate_castling_effectiveness(self):
        data = self.prepare_data()
        fill_value = "-"
        data["whites_best_move_is_castle"] = fill_value
        data["blacks_best_move_is_castle"] = fill_value
        data["whites_best_move"] = fill_value
        data["blacks_best_move"] = fill_value
        data["white_castling_consideration_turn"] = fill_value
        data["black_castling_consideration_turn"] = fill_value

        castling_moves = [chess.Move.from_uci("e1g1"),  # Kingside castling for white: "e1g1"
                          chess.Move.from_uci("e1c1"),  # Queenside castling for white: "e1c1"
                          chess.Move.from_uci("e8g8"),  # Kingside castling for black: "e8g8"
                          chess.Move.from_uci("e8c8"),  # Queenside castling for black: "e8c8"
                          ]

        for index, row in data.iterrows():
            print(f"Analysing row {index + 1}/{len(data.index)}")
            # create a new board and make moves until
            # castling is detected from both players
            # or the game ends
            board = chess.Board()
            moves = eval(row['moves'])
            for move_string in moves:
                move_obj = chess.Move.from_uci(move_string)
                player_color = "white" if board.turn else "black"

                if not board.is_legal(move_obj):
                    print(f"Illegal move in game at row {index}")
                    break

                # check if can castle instead
                for castling_move in castling_moves:
                    if not board.is_legal(castling_move): continue
                    # found a legal castling move
                    # evaluate if it's the best move
                    best_move = self.engine.get_best_move(board, self.limit)

                    is_castling_best = board.is_castling(best_move)
                    data.at[index, f"{player_color}s_best_move_is_castle"] = int(is_castling_best)
                    data.at[index, f"{player_color}s_best_move"] = str(best_move.uci())
                    data.at[index, f"{player_color}_castling_consideration_turn"] = board.fullmove_number

                if data.at[index, f"{player_color}s_best_move_is_castle"] == 1:
                    break

                board.push(move_obj)

        # moves column no longer needed
        data = data.drop(["moves"], axis=1)
        self.__save_to_csv(data, self.output_file)

    def calculate_castling_turns(self):
        data = self.prepare_data()

        for index, row in data.iterrows():
            print(f"Analysing row {index + 1}/{len(data.index)}")
            # create a new board and make moves until
            # castling is detected from both players
            # or the game ends
            board = chess.Board()
            moves = eval(row['moves'])
            for move_string in moves:
                move_obj = chess.Move.from_uci(move_string)

                if not board.is_legal(move_obj):
                    print(f"Illegal move in game at row {index}")
                    break

                if board.is_castling(move_obj):
                    turn_number = board.fullmove_number
                    player_color = "white" if board.turn else "black"

                    data.at[index, f"{player_color}_castle_turn"] = turn_number
                    for check in self.castled_before_checks:
                        data.at[index, f"{player_color}_castled_before_{check}"] = int(turn_number < check)

                # check if castling hasn't been found for both players
                if data.at[index, 'white_castle_turn'] != fill_value and data.at[
                    index, 'black_castle_turn'] != fill_value:
                    break

                board.push(move_obj)

        # moves column no longer needed
        data = data.drop(["moves"], axis=1)
        self.__save_to_csv(data, self.output_file)

# maybe steal?
# def calculate_win_rates(self):
#       data = pd.read_csv(self.output_file)
#
#       print(f"Average castling turn")
#       white_ca = data['white_castle_turn'].apply(lambda x: 0 if x == '-' else int(x)).mean()
#       black_ca = data['black_castle_turn'].apply(lambda x: 0 if x == '-' else int(x)).mean()
#       print(f"W-{white_ca:.2} | B-{black_ca:.2}\n")
#
#       print(f"Base win rate ({len(data.index)} games analysed)")
#       white_wr = data['result'].apply(lambda x: 1 if x == '1-0' else 0).mean()
#       black_wr = data['result'].apply(lambda x: 1 if x == '0-1' else 0).mean()
#       print(f"W-{white_wr:.2%} | B-{black_wr:.2%}")
#
#       for check in self.castled_before_checks:
#           white_games = data[data[f"white_castled_before_{check}"] == 1]
#           white_wr = white_games['result'].apply(
#               lambda x: 1 if x == '1-0' else 0).mean()
#           black_games = data[data[f"black_castled_before_{check}"] == 1]
#           black_wr = black_games['result'].apply(
#               lambda x: 1 if x == '0-1' else 0).mean()
#           print(f"Win rate when castling before move {check} (games analysed)")
#           print(f"W-{white_wr:.2%} ({len(white_games.index)}) | B-{black_wr:.2%} ({len(black_games.index)})")


# def analyse_castling_data(self):
#     # Load data from .csv file
#     df = pd.read_csv("./data/castling_engine.csv")
#     df = df[df[f"white_castling_consideration_turn"] != "-"]
#     df = df[df[f"black_castling_consideration_turn"] != "-"]
#     df = df[df[f"whites_best_move_is_castle"] != "-"]
#     df = df[df[f"blacks_best_move_is_castle"] != "-"]
#
#     # Calculate results
#     total_games = len(df)
#     white_best_move_is_castle = df[df['whites_best_move_is_castle'] == "1"]
#     black_best_move_is_castle = df[df['blacks_best_move_is_castle'] == "1"]
#     games_with_castle_consideration_turn = df[
#         df['white_castling_consideration_turn'].notna() | df['black_castling_consideration_turn'].notna()]
#
#     # Reformat columns
#     df["white_castling_consideration_turn"] = df["white_castling_consideration_turn"].astype(int)
#     df["black_castling_consideration_turn"] = df["black_castling_consideration_turn"].astype(int)
#     df["whites_best_move_is_castle"] = df["whites_best_move_is_castle"].astype(int)
#     df["blacks_best_move_is_castle"] = df["blacks_best_move_is_castle"].astype(int)
#
#     # Convert result values to numerical format
#     result_mapping = {"0-1": -1, "1-0": 1, "1/2-1/2": 0.5}
#     df["result"] = df["result"].map(result_mapping)
#
#     # Group data by castling consideration turn
#     white_grouped = df.groupby("white_castling_consideration_turn").agg(
#         {"whites_best_move_is_castle": ["sum", "count"]})
#     black_grouped = df.groupby("black_castling_consideration_turn").agg(
#         {"blacks_best_move_is_castle": ["sum", "count"]})
#
#     # Calculate the proportion of castlings recommended
#     white_grouped["proportion"] = white_grouped["whites_best_move_is_castle"]["sum"] / \
#                                   white_grouped["whites_best_move_is_castle"]["count"]
#     black_grouped["proportion"] = black_grouped["blacks_best_move_is_castle"]["sum"] / \
#                                   black_grouped["blacks_best_move_is_castle"]["count"]
#
#     # Generate graph
#     plt.figure(figsize=(10, 6))
#     plt.plot(white_grouped.index, white_grouped["proportion"], color="blue", label="White")
#     plt.plot(black_grouped.index, black_grouped["proportion"], color="red", label="Black")
#     plt.xlim(right=45)
#     plt.xlabel("Castling Consideration Turn")
#     plt.ylabel("Proportion of Castlings Recommended")
#     plt.title("Proportion of Castlings Recommended by Castling Consideration Turn")
#     plt.legend()
#     plt.show()
#
#     # Filter results with best move castle
#     results_with_best_move_castle = df[
#         (df['whites_best_move_is_castle'] == 1) | (df['blacks_best_move_is_castle'] == 1)]
#     total_games_with_best_move_castle = len(results_with_best_move_castle)
#
#     # Print results
#     print(f"Total games analyzed: {total_games}")
#     print(f"Total games with best move is castle for White: {len(white_best_move_is_castle)}")
#     print(f"Total games with best move is castle for Black: {len(black_best_move_is_castle)}")
#     print(f"Total games with castling consideration turn: {len(games_with_castle_consideration_turn)}")
#     print(f"Total games with best move castle: {total_games_with_best_move_castle}")
#     print(f"Castling favor ratio: {total_games_with_best_move_castle / len(games_with_castle_consideration_turn):.2%}")
