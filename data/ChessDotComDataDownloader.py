import os
import requests
import json
import chess.pgn
import io
import pandas as pd
import math


# https://www.chess.com/news/view/published-data-api
class ChessDotComDataDownloader:
    def __init__(self, output_file):
        self.output_file = output_file

    # Downloads data of players  with a given title
    # Valid titles are: GM, WGM, IM, WIM, FM, WFM, NM, WNM, CM, WCM.
    # use offset argument to skip first X players in list (in case download was stopped midway)
    def download_data_by_title(self, title, offset=0):
        usernames = self.get_usernames_by_title(title)
        username_count = len(usernames)
        print(f"Found {username_count} {title}\'s")

        for curr_user_index in range(offset, username_count):
            username = usernames[curr_user_index]
            print(f"[{curr_user_index + 1}/{username_count}] Getting data for {username}")
            curr_user_games = self.get_games_by_username(username)
            curr_user_games = self.__combine_months(curr_user_games)
            # curr_user_games = self.__drop_not_required_columns(curr_user_games)

            print(f"Saving to {self.output_file}...")
            self.__save_to_csv(curr_user_games)

        print(f"Download completed")

    def get_games_by_username(self, username):
        archive = self.get_archive_by_username(username)
        months_of_data = len(archive)
        print(f"(found {months_of_data} months worth of games)")

        all_games = []
        for i in range(0, months_of_data):
            url = archive[i]
            print(f"[{i + 1}/{months_of_data}] Fetching {url}...")
            games = self.get_data_from_archive(url)
            df = self.__parse_games(games)
            all_games.append(df)

        return all_games

    @staticmethod
    def get_usernames_by_title(title):
        url = f"https://api.chess.com/pub/titled/{title}"
        data = requests.get(url)
        if data.status_code != 200:
            raise Exception("The following response was returned: " + str(data.status_code))

        data = json.loads(data.text)
        return data["players"]

    # get all the months in which player played any games
    @staticmethod
    def get_archive_by_username(username):
        url = f"https://api.chess.com/pub/player/{username}/games/archives"
        data = requests.get(url)
        if data.status_code != 200:
            raise Exception("The following response was returned: " + str(data.status_code))
        else:
            data = json.loads(data.text)
            return data["archives"]

    # https://api.chess.com/pub/player/{username}/games/{year}/{month}"
    @staticmethod
    def get_data_from_archive(url):
        data = requests.get(url)
        if data.status_code != 200:
            raise Exception("The following response was returned: " + str(data.status_code))

        data = json.loads(data.text)
        return data["games"]

    def __combine_months(self, dfs):
        df = pd.concat(dfs, ignore_index=True)
        return df

    def __drop_not_required_columns(self, df):
        df = df.drop(["termination"], axis=1)
        return df

    def __column_by_month(self, df):
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = pd.DatetimeIndex(df["date"]).month
        return df

    def __save_to_csv(self, df):
        df.to_csv(self.output_file, mode='a', header=not os.path.exists(self.output_file))

    def __parse_games(self, games):
        all_games = []
        for game in games:
            if not game: continue
            if 'pgn' not in game: continue

            pgn = (game['pgn'])
            pgn = io.StringIO(pgn)
            game = chess.pgn.read_game(pgn)
            all_games.append(game)

        game_list = []
        for g in all_games:
            moves = (g.mainline_moves())
            moves = [str(x) for x in moves]

            white = (g.headers['White'])
            black = (g.headers['Black'])
            player_castled = self.contains_castle(g)
            #TODO SAVE ELO
            game = {"date": (g.headers["Date"]), "player_white": white, "player_black": black,
                    "result": (g.headers['Result']), "moves": moves,
                    "no_of_moves": (math.ceil(len(moves) / 2)), "player_castled": player_castled}

            game_list.append(game)

        game_list = pd.DataFrame(game_list)
        return game_list

    # check if any player castled in given game
    def contains_castle(self, game):
        for move in game.mainline_moves():
            if game.board().is_castling(move):
                return True

        return False
