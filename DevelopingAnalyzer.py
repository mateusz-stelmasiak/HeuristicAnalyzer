import os

import pandas as pd

from DataReader import DataReader


class DevelopingAnalyzer(DataReader):

    def __init__(self, data_path):
        super().__init__(data_path)
        self.data_path = data_path
        self.output_file = data_path[:len(data_path) - 4] + "_developing.csv"

    def print_data(self):
        #moves = eval(row['moves'])
        print(str(self.data.columns))
        #print(str(data))
        #data = data.drop(["player_castled", "date", "player_white", "player_black"], axis=1)


