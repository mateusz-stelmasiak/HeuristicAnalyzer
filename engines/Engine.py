from enum import Enum
from sys import platform
import chess
import chess.engine
import os
import time

# ALL CURRENTLY AVAILABLE ENGINES
class EngineType(Enum):
    CRITTER = "Critter"
    GULL = "Gull"
    KOMODO = "Komodo"
    # RYBKA = "Rybka"
    # SJAAKII = "SjaakII"
    STOCKFISH = "Stockfish"
    TOGAIL = "TogaIl"
    ALL = "Wszystkie"


class Engine:
    def __init__(self, engine):
        self.engine = self.__load_engine(engine)
        self.name = engine.name

    def __load_engine(self, engine):
        engine_name = engine.value

        this_path = os.path.dirname(__file__)
        if platform == "win32" or platform == "win64":
            path = os.path.join(this_path, "./Windows/" + engine_name + ".exe")
        elif platform == "linux":
            path = os.path.join(this_path, "./Linux/" + engine_name)

        if path == '':
            return Exception("Platform not supported!")

        engine = chess.engine.SimpleEngine.popen_uci(path)
        engine.configure({'Threads': 3, "Hash": 4096})
        return engine

    def get_best_move(self, board, limit):
        result = self.engine.analysis(board, limit, info=chess.engine.INFO_NONE)
        analysis_res = result.wait()
        return analysis_res.move

    def get_best_move_old(self, board, limit):
        start_time = time.time()
        result = self.engine.play(board, limit, info=chess.engine.INFO_NONE)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"found best move in in {execution_time} seconds.")
        return result.move

    def score_position(self, board, limit, pov):  # handle mates
        info = self.engine.analyse(board, limit)
        score = info["score"]
        if score.is_mate() and abs(score.white().score(mate_score=10)) == 10:
            who_won = score.white().score(mate_score=10)
            if pov is chess.WHITE and who_won == 10:
                return "Gra wygrana!"
            if pov is chess.BLACK and who_won == -10:
                return "Gra wygrana!"

            return "Gra przegrana!"

        if pov is chess.WHITE:
            return score.white().score(mate_score=1000)

        return score.black().score(mate_score=1000)

    # close engine exe when destroying the object
    def __del__(self):
        self.engine.close()
