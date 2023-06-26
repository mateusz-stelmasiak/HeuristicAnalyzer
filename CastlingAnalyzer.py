import os
import chess
import pandas as pd
import numpy as np
from CSVHandler import CSVHandler
from data.processing.BasicStatsGetter import BasicStatsGetter
from engines.Engine import EngineType, Engine
import matplotlib.pyplot as plt
import chess.pgn


# HEURISTIC: "Castle soon (to protect your king and develop your rook)"
class CastlingAnalyzer:

    def __init__(self, sf_depth_limit):
        self.early_turn_cutoff_index = 20 * 2
        # start the search from 5th turn (10 element of the array) as the players cannot castle earlier
        self.earliest_castling_turn_index = 3 * 2
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
            # "WhiteCastlingConsiderationTurn": self.fill_value,
            # "BlackCastlingConsiderationTurn": self.fill_value,
            # "WhiteBestMoveAtConsiderationTurn": self.fill_value,
            # "BlackBestMoveAtConsiderationTurn": self.fill_value,
            # "WhiteShortCastle": self.fill_value,
            # "WhiteLongCastle": self.fill_value,
            # "BlackShortCastle": self.fill_value,
            # "BlackLongCastle": self.fill_value
            "WhiteCastlingConsiderationType": self.fill_value,
            "BlackCastlingConsiderationType": self.fill_value,
        }
        self.empty_result_df = pd.Series(empty_result_dict).to_frame().T

        self.board = chess.Board()
        # self.engine = Engine(EngineType.STOCKFISH)
        # self.limit = chess.engine.Limit(depth=sf_depth_limit)
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
        # analytical_res = self.analytical_method(moves, last_searched_turn)
        empirical_res = self.empirical_method_just_castling_type(moves, last_searched_turn)
        return pd.concat([empirical_res], axis=1)

    def empirical_method(self, moves, last_searched_turn):
        result = {
            "WhiteCastlingConsiderationTurn": self.fill_value,
            "BlackCastlingConsiderationTurn": self.fill_value,
            "WhiteBestMoveAtConsiderationTurn": self.fill_value,
            "BlackBestMoveAtConsiderationTurn": self.fill_value
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

            # both players have lost castling rights, break
            if not self.board.has_castling_rights(True) and not self.board.has_castling_rights(False):
                break

            # this player's has lost castling rights
            if not self.board.has_castling_rights(self.board.turn):
                self.board.push(move_obj)
                continue

            # check if the player can castle instead
            for castling_move in self.castling_move_objects[player_color]:
                if not self.board.is_legal(castling_move):
                    continue

                # found a legal castling move
                # evaluate if it's the best move
                best_move = self.engine.get_best_move(self.board, self.limit)
                if result[f"{player_color}CastlingConsiderationTurn"] == self.fill_value:
                    result[f"{player_color}CastlingConsiderationTurn"] = str(self.board.fullmove_number)
                    result[f"{player_color}BestMoveAtConsiderationTurn"] = str(best_move.uci())
                else:
                    result[f"{player_color}CastlingConsiderationTurn"] = str(result[
                                                                                 f"{player_color}CastlingConsiderationTurn"]) + "," + str(
                        self.board.fullmove_number)
                    result[f"{player_color}BestMoveAtConsiderationTurn"] = result[
                                                                               f"{player_color}BestMoveAtConsiderationTurn"] + "," + str(
                        best_move.uci())
                # castled_flags[player_color] = True

            self.board.push(move_obj)

        return pd.Series(result).to_frame().T

    def empirical_method_just_castling_type(self, moves, last_searched_turn):
        result = {
            "WhiteCastlingConsiderationType": self.fill_value,
            "BlackCastlingConsiderationType": self.fill_value,
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

            # both players have lost castling rights, break
            if not self.board.has_castling_rights(True) and not self.board.has_castling_rights(False):
                break

            # this player's has lost castling rights
            if not self.board.has_castling_rights(self.board.turn):
                self.board.push(move_obj)
                continue

            # check if the player can castle instead
            for castling_move in self.castling_move_objects[player_color]:
                if not self.board.is_legal(castling_move):
                    continue

                # found a legal castling move
                castling_type = "l" if str(castling_move.uci()) == self.castling_moves[
                    f"{str(player_color).lower()}_long_castle"] else "s"
                if result[f"{player_color}CastlingConsiderationType"] == self.fill_value:
                    result[f"{player_color}CastlingConsiderationType"] = castling_type
                else:
                    result[f"{player_color}CastlingConsiderationType"] = str(result[
                                                                                 f"{player_color}CastlingConsiderationType"]) + "," + str(
                        castling_type)

                # castled_flags[player_color] = True

            self.board.push(move_obj)

        return pd.Series(result).to_frame().T

    # empirical method modified for TCEC data
    # we don't need stockfish to check the best move
    # we just check what the engines did
    def empirical_method_TCEC(self, moves, last_searched_turn):
        result = {
            "WhiteCastlingConsiderationTurn": self.fill_value,
            "BlackCastlingConsiderationTurn": self.fill_value,
            "WhiteBestMoveAtConsiderationTurn": self.fill_value,
            "BlackBestMoveAtConsiderationTurn": self.fill_value
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

            # both players have lost castling rights, break
            if not self.board.has_castling_rights(True) and not self.board.has_castling_rights(False):
                break

            # this player's has lost castling rights
            if not self.board.has_castling_rights(self.board.turn):
                self.board.push(move_obj)
                continue

            # check if the player can castle instead
            for castling_move in self.castling_move_objects[player_color]:
                if not self.board.is_legal(castling_move):
                    continue

                # found a legal castling move
                best_move = "-"
                if (turn_index + 1) < len(moves):
                    best_move = moves[turn_index + 1]

                if result[f"{player_color}CastlingConsiderationTurn"] == self.fill_value:
                    result[f"{player_color}CastlingConsiderationTurn"] = str(self.board.fullmove_number)
                    result[f"{player_color}BestMoveAtConsiderationTurn"] = str(best_move.uci())
                else:
                    result[f"{player_color}CastlingConsiderationTurn"] = str(result[
                                                                                 f"{player_color}CastlingConsiderationTurn"]) + "," + str(
                        self.board.fullmove_number)
                    result[f"{player_color}BestMoveAtConsiderationTurn"] = result[
                                                                               f"{player_color}BestMoveAtConsiderationTurn"] + "," + str(
                        best_move.uci())

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

    def analyze_empirical_results(self, result_path, output_path):
        print("Empirical result analysis started")
        print("Loading data...")
        csv_handler = CSVHandler(result_path, output_path)
        df = csv_handler.data

        print("Manipulating data...")
        bsg = BasicStatsGetter()

        print(f"All data len{len(df)}")
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df)
        print(f"{white_wr},{black_wr},{draw_rate}")

        white_castling_considered = df[df['WhiteBestMoveAtConsiderationTurn'] != "-"]
        black_castling_considered = df[df['BlackBestMoveAtConsiderationTurn'] != "-"]
        print(white_castling_considered.columns)
        print(black_castling_considered.columns)
        # Convert the comma-separated strings into lists
        white_castling_considered['WhiteBestMoveAtConsiderationTurn'] = white_castling_considered[
            'WhiteBestMoveAtConsiderationTurn'].apply(lambda x: x.split(','))
        white_castling_considered['WhiteCastlingConsiderationTurn'] = white_castling_considered[
            'WhiteCastlingConsiderationTurn'].apply(lambda x: x.split(','))
        white_castling_considered['WhiteCastlingConsiderationType'] = white_castling_considered[
            'WhiteCastlingConsiderationType'].apply(lambda x: x.split(','))
        black_castling_considered['BlackBestMoveAtConsiderationTurn'] = black_castling_considered[
            'BlackBestMoveAtConsiderationTurn'].apply(lambda x: x.split(','))
        black_castling_considered['BlackCastlingConsiderationTurn'] = black_castling_considered[
            'BlackCastlingConsiderationTurn'].apply(lambda x: x.split(','))
        black_castling_considered['BlackCastlingConsiderationType'] = black_castling_considered[
            'BlackCastlingConsiderationType'].apply(lambda x: x.split(','))
        mismatch_counter = 0
        # Calculate the percentage of best moves that are castling moves for each turn
        print(
            f"tura,procent roszad jako najlepsze ruchy białego, gier w których możliwe było roszwanie białych w tym ruchu,najlepszych krótkich roszad białego,rozważanych krótkich roszad białego,procent najlepszych krótkich roszad białego,najlepszych długich roszad białego,rozważanych długich roszad białęgo,procent najlepszych długich roszad białego"
            f"procent roszad jako najlepsze ruchy czarnego, gier w których możliwe było roszwanie czarnych w tym ruchu,najlepszych krótkich roszad czarnego,rozważanych krótkich roszad czarnego,procent najlepszych krótkich roszad czarnego,najlepszych długich roszad czarnego,rozważanych długich roszad czarnego,procent najlepszych długich roszad czarnego")
        for turn in range(4, 16):
            short_castle_considered_white = 0
            long_castle_considered_white = 0
            best_move_short_castle_white_games = 0
            best_move_long_castle_white_games = 0
            short_castle_considered_black = 0
            long_castle_considered_black = 0
            best_move_short_castle_black_games = 0
            best_move_long_castle_black_games = 0

            for index, row in black_castling_considered.iterrows():
                for x in range(len(row['BlackCastlingConsiderationTurn'])):
                    if str(turn) == row['BlackCastlingConsiderationTurn'][x]:
                        best_move = row['BlackBestMoveAtConsiderationTurn'][x]
                        if x >= len(row['BlackCastlingConsiderationType']):
                            print(row)
                            return
                            mismatch_counter+=1
                            #print("mismatch")
                            break
                        #print("match")
                        castling_type = row['BlackCastlingConsiderationType'][x]
                        if castling_type == "l":
                            long_castle_considered_black += 1
                        else:
                            short_castle_considered_black += 1

                        if best_move == self.castling_moves['black_short_castle']:
                            best_move_short_castle_black_games += 1
                            break

                        if best_move == self.castling_moves['black_long_castle']:
                            best_move_long_castle_black_games += 1

                        break

            for index, row in white_castling_considered.iterrows():
                for x in range(len(row['WhiteCastlingConsiderationTurn'])):
                    if str(turn) == row['WhiteCastlingConsiderationTurn'][x]:
                        best_move = row['WhiteBestMoveAtConsiderationTurn'][x]
                        if x >= len(row['WhiteCastlingConsiderationType']):
                            mismatch_counter+=1
                            break

                        castling_type = row['WhiteCastlingConsiderationType'][x]
                        if castling_type == "l":
                            long_castle_considered_white += 1
                        else:
                            short_castle_considered_white += 1

                        if best_move == self.castling_moves['white_short_castle']:
                            best_move_short_castle_white_games += 1
                            break

                        if best_move == self.castling_moves['white_long_castle']:
                            long_castle_considered_white += 1

                        break

            # Calculate percentages, handling division by zero
            if short_castle_considered_white + long_castle_considered_white == 0:
                white_castle_percent = 0
            else:
                white_castle_percent = float((best_move_short_castle_white_games + best_move_long_castle_white_games) / (
                        short_castle_considered_white + long_castle_considered_white))

            if short_castle_considered_white == 0:
                white_short_castle_percent = 0
            else:
                white_short_castle_percent = best_move_short_castle_white_games / short_castle_considered_white

            if long_castle_considered_white == 0:
                white_long_castle_percent = 0
            else:
                white_long_castle_percent = best_move_long_castle_white_games / long_castle_considered_white

            if long_castle_considered_black + short_castle_considered_black == 0:
                black_castle_percent = 0
            else:
                black_castle_percent = (best_move_short_castle_black_games + best_move_long_castle_black_games) / (
                        long_castle_considered_black + short_castle_considered_black)

            if short_castle_considered_black == 0:
                black_short_castle_percent = 0
            else:
                black_short_castle_percent = best_move_short_castle_black_games / short_castle_considered_black

            if long_castle_considered_black == 0:
                black_long_castle_percent = 0
            else:
                black_long_castle_percent = best_move_long_castle_black_games / long_castle_considered_black

            print(
                f"{turn},{white_castle_percent},{short_castle_considered_white + long_castle_considered_white},{best_move_short_castle_white_games},{short_castle_considered_white},{white_short_castle_percent},{best_move_long_castle_white_games},{long_castle_considered_white},{white_long_castle_percent},"
                f"{black_castle_percent},{long_castle_considered_black + short_castle_considered_black},{best_move_short_castle_black_games},{short_castle_considered_black},{black_short_castle_percent},{best_move_long_castle_black_games},{long_castle_considered_black},{black_long_castle_percent}"
            )

        print(mismatch_counter)

                # # Calculate the percentage of best moves that are castling moves for each game
                # white_castling_considered = white_castling_considered.apply(
                #     lambda moves: sum(1 for move in moves if move in self.castling_moves.values()) / len(moves) if moves else 0
                # )
                # black_castling_considered = black_castling_considered.apply(
                #     lambda moves: sum(1 for move in moves if move in self.castling_moves.values()) / len(moves) if moves else 0
                # )
                #
                # # Calculate the average of BestWhiteMoveIsCastlePercent and BestBlackMoveIsCastlePercent for all games
                # avg_best_white_move_is_castle_percent = white_castling_considered.mean()
                # avg_best_black_move_is_castle_percent = black_castling_considered.mean()
                #
                # print(f"Average BestWhiteMoveIsCastlePercent: {avg_best_white_move_is_castle_percent}")
                # print(f"Average BestBlackMoveIsCastlePercent: {avg_best_black_move_is_castle_percent}")
                #
                # # Save the results to the output CSV
                # df['BestWhiteMoveIsCastlePercent'] = white_castling_considered
                # df['BestBlackMoveIsCastlePercent'] = black_castling_considered
                # csv_handler.save_to_csv(df)

    def analyze_results(self, result_path, output_path, max_turn):
        print("Result analysis started")
        print("Loading data...")
        csv_handler = CSVHandler(result_path, output_path)
        df = csv_handler.data

        print("Manipulating data...")
        # Convert castle turn columns to string type
        # for column in ['WhiteShortCastle', 'WhiteLongCastle', 'BlackShortCastle', 'BlackLongCastle']:
        #     df[column] = df[column].astype(dtype=str)
        print(df.columns)
        bsg = BasicStatsGetter()

        print(f"All data len{len(df)}")
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df)
        print(f"{white_wr},{black_wr},{draw_rate}")

        # Filter just games with any white castle (short or long)
        df_white_any_castle = df[(df['WhiteShortCastle'] != "-") | (df['WhiteLongCastle'] != "-")]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_any_castle)
        print(f"Any white castle [W,B,D] len{len(df_white_any_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")
        print(f"{len(df_white_any_castle) / len(df):.2%}")

        # Filter just games with white short castle
        df_white_short_castle = df[df['WhiteShortCastle'] != "-"]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_short_castle)
        print(f"White short castle [W,B,D] len{len(df_white_short_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")
        print(f"{len(df_white_short_castle) / len(df_white_any_castle):.2%}")

        # Filter just games with white long castle
        df_white_long_castle = df[df['WhiteLongCastle'] != "-"]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_long_castle)
        print(f"White long castle [W,B,D] len{len(df_white_long_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")
        print(f"{len(df_white_long_castle) / len(df_white_any_castle):.2%}")

        # Filter just games with no castle
        df_white_no_castle = df[(df['WhiteShortCastle'] == "-") & (df['WhiteLongCastle'] == "-")]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_no_castle)
        print(f"No white castle [W,B,D] len{len(df_white_no_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")

        # Same (3) for black
        df_black_any_castle = df[(df['BlackShortCastle'] != "-") | (df['BlackLongCastle'] != "-")]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_any_castle)
        print(f"Any black castle [W,B,D] len{len(df_black_any_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")
        print(f"{len(df_black_any_castle) / len(df):.2%}")

        df_black_short_castle = df[df['BlackShortCastle'] != "-"]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_short_castle)
        print(f"Short black castle [W,B,D] len{len(df_black_short_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")
        print(f"{len(df_black_short_castle) / len(df_black_any_castle):.2%}")

        df_black_long_castle = df[df['BlackLongCastle'] != "-"]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_long_castle)
        print(f"Long black castle [W,B,D] len{len(df_black_long_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")
        print(f"{len(df_black_long_castle) / len(df_black_any_castle):.2%}")

        df_black_no_castle = df[(df['BlackShortCastle'] == "-") & (df['BlackLongCastle'] == "-")]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_no_castle)
        print(f"NO black castle [W,B,D] len{len(df_black_no_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")

        # Find games in which white castled (short or long) and black didn't
        df_white_castle_black_no_castle = df[((df['WhiteShortCastle'] != "-") | (df['WhiteLongCastle'] != "-")) &
                                             ((df['BlackShortCastle'] == "-") & (df['BlackLongCastle'] == "-"))]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_castle_black_no_castle)
        print(f"White castle, black no castle [W,B,D] len{len(df_white_castle_black_no_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")

        # Find games in which black castled (short or long) and white didn't
        df_black_castle_white_no_castle = df[((df['BlackShortCastle'] != "-") | (df['BlackLongCastle'] != "-")) &
                                             ((df['WhiteShortCastle'] == "-") & (df['WhiteLongCastle'] == "-"))]
        white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_castle_white_no_castle)
        print(f"Black castle, white no castle [W,B,D] len{len(df_black_castle_white_no_castle)}")
        print(f"{white_wr},{black_wr},{draw_rate}")

        # Filter just games with no castle

        # Convert castle turn columns to numeric type (errors='coerce' will turn non-numeric values into NaN)
        for column in ['WhiteShortCastle', 'WhiteLongCastle', 'BlackShortCastle', 'BlackLongCastle']:
            df[column] = pd.to_numeric(df[column], errors='coerce')

        print(f"White ALL castle at turn {max_turn}  [W,B,D]")
        # Calculate and display win rate for each castling turn (any castle, short or long) for white (turns 4 through 15)
        for turn in range(4, max_turn):
            df_white_castle_turn = df[(df['WhiteShortCastle'] == turn) | (df['WhiteLongCastle'] == turn)]
            white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_castle_turn)
            # print(f"White castle at turn {turn}  [W,B,D] len{len(df_white_castle_turn)}")
            print(f"{white_wr},{len(df_white_castle_turn)}")

        print(f"Black ALL castle at turn {max_turn}  [W,B,D]")
        # Calculate and display win rate for each castling turn (any castle, short or long) for black (turns 4 through 15)
        for turn in range(4, max_turn):
            df_black_castle_turn = df[(df['BlackShortCastle'] == turn) | (df['BlackLongCastle'] == turn)]
            white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_castle_turn)
            # print(f"Black castle at turn {turn}  [W,B,D] len{len(df_black_castle_turn)}")
            print(f"{black_wr},{len(df_black_castle_turn)}")

        print(f"White short castle at turn {max_turn}  [W,B,D]")
        # Calculate and display win rate for each castling turn (just short castle) for white (turns 4 through 15)
        for turn in range(4, max_turn):
            df_white_short_castle_turn = df[df['WhiteShortCastle'] == turn]
            white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_short_castle_turn)
            # print(f"White short castle at turn {turn}  [W,B,D] len{len(df_white_short_castle_turn)}")
            print(f"{white_wr},{len(df_white_short_castle_turn)}")

        # Calculate and display win rate for each castling turn (just long castle) for white (turns 4 through 15)
        print(f"White LONG castle at turn {max_turn}  [W,B,D]")
        for turn in range(4, max_turn):
            df_white_short_castle_turn = df[df['WhiteLongCastle'] == turn]
            white_wr, black_wr, draw_rate = bsg.get_win_rates(df_white_short_castle_turn)
            # print(f"White short castle at turn {turn}  [W,B,D] len{len(df_white_short_castle_turn)}")
            print(f"{white_wr},{len(df_white_short_castle_turn)}")
            # Calculate and display win rate for each castling turn (just long castle) for black (turns 4 through 15)

        print(f"BLACK short castle at turn {max_turn}  [W,B,D]")
        for turn in range(4, max_turn):
            df_black_long_castle_turn = df[df['BlackShortCastle'] == turn]
            white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_long_castle_turn)
            # print(f"Black long castle at turn {turn}  [W,B,D] len{len(df_black_long_castle_turn)}")
            print(f"{black_wr},{len(df_black_long_castle_turn)}")

        # Calculate and display win rate for each castling turn (just long castle) for black (turns 4 through 15)
        print(f"Black long castle at turn max_turn  [W,B,D]")
        for turn in range(4, max_turn):
            df_black_long_castle_turn = df[df['BlackLongCastle'] == turn]
            white_wr, black_wr, draw_rate = bsg.get_win_rates(df_black_long_castle_turn)
            # print(f"Black long castle at turn {turn}  [W,B,D] len{len(df_black_long_castle_turn)}")
            print(f"{black_wr},{len(df_black_long_castle_turn)}")

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
