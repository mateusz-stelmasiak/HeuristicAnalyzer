import CSVHandler
import numpy as np


class DataPreparator:

    def __init__(self, input_path, output_path):
        print(f"Loading data from file...")
        self.csv_handler = CSVHandler.CSVHandler(input_path, output_path)
        print(f"Loaded {len(self.csv_handler.data)} games")
        return

    # chooses n_of_games_to_extract, random games and saves them into
    # a separate csv file
    def prepare_data(self, n_of_games_to_extract):
        df = self.csv_handler.data
        if n_of_games_to_extract > len(df):
            print("Number of games to extract is greater than the total number of games. Extracting all games instead.")
            n_of_games_to_extract = len(df)

        print(f"Choosing a random sample of {n_of_games_to_extract} games...")
        extracted_games = df.sample(n_of_games_to_extract)
        print(f"Saving to CSV...")
        self.csv_handler.save_to_csv(extracted_games)

    # takes an optional "distribution" array and splits the ammount of data in each file accordin to it
    # ex. split_into_files(3,[0.2,0.2,0.6]) would split the data into 3 files, first two containing 20% of
    # the data and the last one containing 60%
    def split_into_files(self, n_of_files, distribution=None):
        df = self.csv_handler.data

        print(f"Splitting the data...")
        if distribution is None:
            # If no distribution is provided, split the data evenly
            split_dfs = np.array_split(df, n_of_files)
        else:
            # If a distribution is provided, split the data according to the distribution
            if len(distribution) != n_of_files:
                raise ValueError("Length of distribution array must be equal to n_of_files")
            if not np.isclose(sum(distribution), 1):
                raise ValueError("Sum of distribution array must be equal to 1")

            split_dfs = []
            start = 0
            for dist in distribution:
                end = start + int(dist * len(df))
                split_dfs.append(df.iloc[start:end])
                start = end

        print(f"Saving to separate CSV files...")
        for i, split_df in enumerate(split_dfs):
            output_path = self.csv_handler.output_path.replace('.csv', f'_{i}.csv')
            self.csv_handler.save_to_csv(split_df, output_path)


