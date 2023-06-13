import os

import pandas as pd


class CSVHandler:

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.__load_data()
        self.__clean_data()

    def __load_data(self):
        dtype = {"WhiteElo": int, "BlackElo": int, "Result": str, "Moves": str}
        self.data = pd.read_csv(self.input_path, dtype=dtype)

    def delete_output_file(self):
        if not os.path.isfile(self.output_path):
            return

        os.remove(self.output_path)

    def append_to_csv(self, df):
        df.to_csv(self.output_path, mode='a', header=not os.path.exists(self.output_path),index=False)

    def __clean_data(self):
        self.data = self.data.dropna()  # Remove rows with missing values
