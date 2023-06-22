import pandas as pd

# Wczytanie pliku CSV do pandas DataFrame
df = pd.read_csv('../../../../results/developing/developing_empirical_elite_data_results.csv')

# Obliczenie procentowego udziału ruchów rozwijających figury
df['BestPieceMovesPercentageWhite'] = (df['BestPieceMovesCountWhite'] / df['ConsideredMovesWhite']) * 100
df['BestPieceMovesPercentageBlack'] = (df['BestPieceMovesCountBlack'] / df['ConsideredMovesBlack']) * 100

# Obliczenie średniej procentowego udziału ruchów rozwijających figury
mean_white = df['BestPieceMovesPercentageWhite'].mean()
mean_black = df['BestPieceMovesPercentageBlack'].mean()

print("Średnia procentowego udziału ruchów rozwijających figury dla białych: ", mean_white)
print("Średnia procentowego udziału ruchów rozwijających figury dla czarnych: ", mean_black)