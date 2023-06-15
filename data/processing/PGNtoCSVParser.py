import chess.pgn
from os import listdir
from os.path import isfile, join


class PGNtoCSVParser:
    def __init__(self, output_file):
        self.output_file = output_file

    def parse_all_in_folder(self, path, limit=None, max_elo_diff=None, max_elo=None):
        file_list = [f for f in listdir(path) if isfile(join(path, f))]
        file_num = len(file_list)
        output_file_obj = open(self.output_file, 'a')
        output_file_obj.write('WhiteElo,BlackElo,Result,Moves\n')
        output_file_obj.close()

        for i in range(0, file_num):
            curr_file = file_list[i]
            if not curr_file.endswith(".pgn"):
                print(f"[{i + 1}/{file_num}] \"{curr_file}\" is not a pgn file, next")
                continue

            print(f"[{i + 1}/{file_num}] Parsing \"{curr_file}\"...")
            self.parse_png(f"{path}/{curr_file}", limit=limit, max_elo_diff=max_elo_diff, max_elo=max_elo)

    def parse_png(self, path, limit=None, max_elo_diff=None, max_elo=None):
        input_file = open(path)
        output_file_obj = open(self.output_file, 'a')
        counter = 0
        while True:
            print(f"[{counter}/XX] Parsing a new game...")
            game = chess.pgn.read_game(input_file)

            if game is None:
                break  # end of file

            if limit and counter == limit:
                break  # limit reached

            if 'WhiteElo' not in game.headers or 'BlackElo' not in game.headers or 'Result' not in game.headers:
                print(f"Found game with missing headers")
                continue

            # skip bullets and unrated
            g_type = game.headers['Event']
            if 'Rated' not in g_type or 'Bullet' in g_type:
                print(f"Skipping: Wrong game type {game.headers['Event']}")
                continue

            # skip unrated players
            if game.headers['WhiteElo'] == '?' or game.headers['BlackElo'] == '?':
                print(f"Skipping: Unrated players")
                continue

            white_elo = int(game.headers['WhiteElo'])
            black_elo = int(game.headers['BlackElo'])

            # skip ELO too high
            if max_elo and (white_elo >= max_elo or black_elo >= max_elo):
                print(f"Skipping: ELO above max")
                continue

            # skip games with too high elo diff
            if max_elo_diff and abs(white_elo - black_elo) >= max_elo_diff:
                print(f"Skipping: Elo diff too high")
                continue

            moves = (game.mainline_moves())
            moves = [str(x) for x in moves]
            relevant_data = f"{white_elo},{black_elo},{game.headers['Result']},\"{moves}\"\n"

            output_file_obj.write(relevant_data)
            counter = counter + 1

        input_file.close()
        output_file_obj.close()
