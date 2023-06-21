import numpy as np
import pandas as pd

# Określ przewagę w rozwoju jako rozwinięcie co najmniej dwóch figur więcej
development_lead = 3

# Wczytanie pliku CSV do pandas DataFrame
df = pd.read_csv('../../../../results/developing/developing_analytic_TCEC_data_results.csv')

df['EarliestWhitePieceMove'] = df[['WhiteKnight_b1','WhiteKnight_g1','WhiteBishop_c1','WhiteBishop_f1']].min(axis=1)
df['EarliestBlackPieceMove'] = df[['BlackKnight_b8','BlackKnight_g8','BlackBishop_c8','BlackBishop_f8']].min(axis=1)

df = df[df['Result'] != '*']
df['Result'] = df['Result'].replace({'1-0': 1, '0-1': -1, '1/2-1/2': 0}).astype(float)

df['WhiteDeveloped'] = (df[['WhiteKnight_b1', 'WhiteKnight_g1', 'WhiteBishop_c1', 'WhiteBishop_f1']] <= 6).sum(axis=1)
df['BlackDeveloped'] = (df[['BlackKnight_b8', 'BlackKnight_g8', 'BlackBishop_c8', 'BlackBishop_f8']] <= 6).sum(axis=1)

df['DevelopmentAdvantage'] = np.where(df['WhiteDeveloped'] - df['BlackDeveloped'] > development_lead, 'White',
                                      np.where(df['BlackDeveloped'] - df['WhiteDeveloped'] > development_lead, 'Black', 'None'))

winning_results = df[df['Result'] > 0].groupby('DevelopmentAdvantage')['Result'].count() / df.groupby('DevelopmentAdvantage')['Result'].count() * 100

# Dodajemy obliczanie procentu remisów
draw_results = df[df['Result'] == 0].groupby('DevelopmentAdvantage')['Result'].count() / df.groupby('DevelopmentAdvantage')['Result'].count() * 100

# Dodajemy linię kodu, która wyświetla ilość gier z daną przewagą w rozwoju
games_count = df.groupby('DevelopmentAdvantage')['Result'].count()

print("Percentage of games won:")
print(winning_results)
print("\nPercentage of games drawn:")
print(draw_results)
print("\nNumber of games:")
print(games_count)