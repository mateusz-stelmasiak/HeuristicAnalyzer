from CSVHandler import CSVHandler
import matplotlib.pyplot as plt
import pandas as pd


class BasicStatsGetter:
    def __init__(self):
        return

    def get_basic_stats(self, data_path,data_set_name):
        # read data from file
        data_reader = CSVHandler(data_path)
        print(f"Analysing {len(data_reader.data)} games...")

        white_wr, black_wr, draw_rate = self.get_win_rates(data_reader.data)
        print(f"WIN RATES")
        print(f"W-{white_wr:.2%} | B-{black_wr:.2%} | D-{draw_rate:.2%}")
        self.draw_wr_piechart(white_wr, black_wr, draw_rate,data_set_name)

        white_elo_avr, black_elo_avr, white_elo_std, black_elo_std, all_elo_avr, all_elo_std = self.get_elo_distribution(
            data_reader.data)
        print(f"ELO STATS")
        print(f"~{all_elo_avr:.2f} std. {all_elo_std:.2f}")
        print(
            f"W- avr. {white_elo_avr:.2f} std. {white_elo_std:.2f} | B- avr. {black_elo_avr:.2f} std. {black_elo_std:.2f}")
        self.draw_elo_histogram(data_reader.data,data_set_name)

    def get_elo_distribution(self, data):
        # calculate mean of WhiteELo and BlackElo
        white_elo_avr = data['WhiteElo'].mean()
        black_elo_avr = data['BlackElo'].mean()

        # Calculate standard deviation of WhiteElo and BlackElo
        white_elo_std = data['WhiteElo'].std()
        black_elo_std = data['BlackElo'].std()

        # Concatenate WhiteElo and BlackElo into a single series
        all_elo = pd.concat([data['WhiteElo'], data['BlackElo']])

        # Calculate mean and standard deviation of all ELO
        all_elo_avr = all_elo.mean()
        all_elo_std = all_elo.std()

        return white_elo_avr, black_elo_avr, white_elo_std, black_elo_std, all_elo_avr, all_elo_std

    def get_win_rates(self, data):
        white_wr = data['Result'].apply(lambda x: 1 if x == '1-0' else 0).mean()
        black_wr = data['Result'].apply(lambda x: 1 if x == '0-1' else 0).mean()
        draw_rate = data['Result'].apply(lambda x: 1 if x == '1/2-1/2' else 0).mean()
        return white_wr, black_wr, draw_rate

    def draw_wr_piechart(self, white_wr, black_wr, draw_rate,data_set_name):
        # Data to plot
        labels = 'Wygrane białych', 'Wygrane czarnych', 'Remisy'
        sizes = [white_wr, black_wr, draw_rate]
        colors = ['#e8fcff','#00425c', '#769ba8']


        # Plot
        wedges, texts,_ = plt.pie(sizes,
                                colors=colors,
                                startangle=160,
                                autopct='%1.1f%%',
                                shadow=True,
                                  )

        # Add a legend
        plt.legend(wedges, labels, loc="upper right")
        plt.title(f"Wyniki rozgrywek w partiach {data_set_name}")

        # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.axis('equal')

        plt.show()

    def draw_elo_histogram(self, data,data_set_name):
        # Create subplots
        all_elo = pd.concat([data['WhiteElo'], data['BlackElo']])

        plt.hist(all_elo, bins=60, alpha=0.9,color="#00425c")
        plt.xlabel("punkty ELO")
        plt.ylabel("liczba graczy")
        plt.title(f"Rozkład ELO w partiach {data_set_name}")
        plt.show()
