import os

import pandas as pd


class DataReader:

    def __init__(self, data_path):
        self.data_path = data_path
        self.__load_data()
        self.__drop_unnecessary_columns()
        self.__clean_data()

    def __load_data(self):
        self.data = pd.read_csv(self.data_path)

    def save_to_csv(self, df, filename):
        df.to_csv(filename, mode='a', header=not os.path.exists(filename))

    def __drop_unnecessary_columns(self):
        self.data_path = self.data.drop(["player_castled", "date", "player_white", "player_black"], axis=1)

    def __clean_data(self):
        self.data = self.data.dropna()  # Remove rows with missing values
