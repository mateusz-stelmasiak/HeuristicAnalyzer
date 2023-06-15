import os

import pandas as pd
from multiprocessing import Manager


class CSVHandler:

    def __init__(self, input_path, output_path=None):
        self.input_path = input_path
        self.output_path = output_path
        self.__load_data()
        self.__clean_data()
        self.lock = Manager().Lock()

    def __load_data(self):
        dtype = {"WhiteElo": int, "BlackElo": int, "Result": str, "Moves": str}
        self.data = pd.read_csv(self.input_path, dtype=dtype)

    def delete_output_file(self):
        if not os.path.isfile(self.output_path):
            return

        os.remove(self.output_path)

    def append_to_csv(self, df):
        with self.lock:
            df.to_csv(self.output_path, mode='a', header=not os.path.exists(self.output_path), index=False)

    def save_to_csv(self, df, output_path=None):
        if not output_path:
            df.to_csv(self.output_path, index=False)
            return
        df.to_csv(output_path, index=False)

    def __clean_data(self):
        self.data = self.data.dropna()  # Remove rows with missing values
