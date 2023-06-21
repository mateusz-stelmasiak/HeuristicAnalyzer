import pandas as pd

fileName = "../../subeliteMoves"

# Wczytaj plik CSV
df = pd.read_csv(fileName + ".csv")

# Usuń powtórzenia na podstawie kolumny "FEN"
df_unique = df.drop_duplicates(subset='FEN')

# Zapisz wyniki do nowego pliku CSV
df_unique.to_csv(fileName + "_cleaned.csv", index=False)
