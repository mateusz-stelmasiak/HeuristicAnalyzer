import os
import chess
import pandas as pd
from engines.Engine import EngineType, Engine
import matplotlib.pyplot as plt


# HEURISTIC: "Castle soon (to protect your king and develop your rook)"
class CastlingAnalyzer:

    def __init__(self, engine, limit):
        self.early_turn_cutoff_index = 15 * 2
        # start the search from 5th turn (10 element of the array) as the players cannot castle earlier
        self.earliest_castling_turn_index = 5 * 2
        self.fill_value = "-"  # value that is put if player didn't castle at all
        self.castling_moves = {
            "white_short_castle": "e1g1",
            "white_long_castle": "e1c1",
            "black_short_castle": "e8g8",
            "black_long_castle": "e8c8"
        }
        self.white_castling_moves = [self.castling_moves['white_short_castle'],
                                     self.castling_moves["white_long_castle"]]
        self.white_castling_types = ["WhiteShortCastle", "WhiteLongCastle"]
        self.black_castling_moves = [self.castling_moves['black_short_castle'],
                                     self.castling_moves["black_long_castle"]]
        self.black_castling_types = ["BlackShortCastle", "BlackLongCastle"]

        empty_result_dict = {
            "WhiteCastlingConsiderationTurn": self.fill_value,
            "BlackCastlingConsiderationTurn": self.fill_value,
            "WhiteBestMoveAtConsiderationTurn": self.fill_value,
            "BlackBestMoveAtConsiderationTurn": self.fill_value,
            "WhiteShortCastle": self.fill_value,
            "WhiteLongCastle": self.fill_value,
            "BlackShortCastle": self.fill_value,
            "BlackLongCastle": self.fill_value
        }
        self.empty_result_df = pd.Series(empty_result_dict).to_frame().T

        self.board = chess.Board()
        self.limit = limit
        self.engine = engine
        self.castling_move_objects = {
            "White": [chess.Move.from_uci(self.castling_moves['white_short_castle']),
                      chess.Move.from_uci(self.castling_moves['white_long_castle']),
                      ],
            "Black": [chess.Move.from_uci(self.castling_moves['black_short_castle']),
                      chess.Move.from_uci(self.castling_moves['black_long_castle'])]
        }

    def analyze_game(self, moves):
        # if game didn't even last long enough to castle, don't even start the analysis
        move_number = len(moves)
        if move_number < self.earliest_castling_turn_index:
            return self.empty_result_df

        # end search where 'early' is defined or at the last turn
        last_searched_turn = min(self.early_turn_cutoff_index, move_number)
        analytical_res = self.analytical_method(moves, last_searched_turn)
        #empirical_res = self.empirical_method(moves, last_searched_turn)
        return pd.concat([analytical_res], axis=1)

    def empirical_method(self, moves, last_searched_turn):
        result = {
            "WhiteCastlingConsiderationTurn": self.fill_value,
            "BlackCastlingConsiderationTurn": self.fill_value,
            "WhiteBestMoveAtConsiderationTurn": self.fill_value,
            "BlackBestMoveAtConsiderationTurn": self.fill_value
        }
        castled_flags = {
            "White": False,
            "Black": False
        }

        # set up the board and make move up to earliest castling turn
        self.board.reset()
        for i in range(0, self.earliest_castling_turn_index):
            curr_move = moves[i]
            move_obj = chess.Move.from_uci(curr_move)
            self.board.push(move_obj)

        for turn_index in range(self.earliest_castling_turn_index, last_searched_turn):
            curr_move = moves[turn_index]
            move_obj = chess.Move.from_uci(curr_move)
            player_color = "White" if self.board.turn else "Black"

            if not self.board.is_legal(move_obj):
                print(f"Illegal move found in game!")
                break

            # found for both
            if castled_flags["Black"] and castled_flags["White"]:
                break

            # this player's castling, has already been considered
            if castled_flags[player_color]:
                self.board.push(move_obj)
                continue

            # check if the player can castle instead
            for castling_move in self.castling_move_objects[player_color]:
                if not self.board.is_legal(castling_move):
                    continue

                # found a legal castling move
                # evaluate if it's the best move
                best_move = self.engine.get_best_move_old(self.board, self.limit)
                result[f"{player_color}CastlingConsiderationTurn"] = self.board.fullmove_number
                result[f"{player_color}BestMoveAtConsiderationTurn"] = str(best_move.uci())
                castled_flags[player_color] = True

            self.board.push(move_obj)

        return pd.Series(result).to_frame().T

    def analytical_method(self, moves, last_searched_turn):
        # print(f"Looking for castling in {moves}")
        result = {
            "WhiteShortCastle": self.fill_value,
            "WhiteLongCastle": self.fill_value,
            "BlackShortCastle": self.fill_value,
            "BlackLongCastle": self.fill_value
        }
        white_castled_flag = False
        black_castled_flag = False
        white_turn = False  # set to false so it can be flipped at the begining of the loop

        for turn_index in range(self.earliest_castling_turn_index, last_searched_turn):
            curr_move = moves[turn_index]
            white_turn = not white_turn
            # print(f"Looking at {curr_move} (index {turn_index})")

            if white_castled_flag and black_castled_flag:
                break

            # check for white castle
            if white_turn and not white_castled_flag:
                castling_type_index = self.white_castling_moves.index(
                    curr_move) if curr_move in self.white_castling_moves else None

                if castling_type_index is not None:
                    castling_type = self.white_castling_types[castling_type_index]
                    result[castling_type] = turn_index // 2 + 1
                    white_castled_flag = True
                    continue

            if not white_turn and not black_castled_flag:
                castling_type_index = self.black_castling_moves.index(
                    curr_move) if curr_move in self.black_castling_moves else None

                if castling_type_index is not None:
                    castling_type = self.black_castling_types[castling_type_index]
                    result[castling_type] = turn_index // 2 + 1
                    black_castled_flag = True
                    continue

        return pd.Series(result).to_frame().T

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
