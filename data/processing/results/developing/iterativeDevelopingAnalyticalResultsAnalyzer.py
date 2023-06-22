import pandas as pd
import numpy as np

# Wczytanie pliku CSV do pandas DataFrame
df = pd.read_csv('../../../../results/developing/developing_analytic_elite_data_results.csv')

df = df[df['Result'] != '*']
df['Result'] = df['Result'].replace({'1-0': 1, '0-1': -1, '1/2-1/2': 0}).astype(float)


for development_lead in range(1,5):
    results_list = []
    for turn in range(6, int(27)):
        df['WhiteDeveloped'] = (
                    df[['WhiteKnight_b1', 'WhiteKnight_g1', 'WhiteBishop_c1', 'WhiteBishop_f1']] <= turn).sum(axis=1)
        df['BlackDeveloped'] = (
                    df[['BlackKnight_b8', 'BlackKnight_g8', 'BlackBishop_c8', 'BlackBishop_f8']] <= turn).sum(axis=1)

        df['DevelopmentAdvantage'] = np.where(df['WhiteDeveloped'] - df['BlackDeveloped'] == development_lead, 'White',
                                              np.where(df['BlackDeveloped'] - df['WhiteDeveloped'] == development_lead,
                                                       'Black', 'None'))

        total_games = df.groupby('DevelopmentAdvantage')['Result'].count()
        winning_results = df[df['Result'] > 0].groupby('DevelopmentAdvantage')['Result'].count() / total_games * 100
        draw_results = df[df['Result'] == 0].groupby('DevelopmentAdvantage')['Result'].count() / total_games * 100

        results_list.append({
            'turn': turn,
            'development_lead': development_lead,
            'white_win_%': winning_results.get('White', np.nan),
            'white_draw_%': draw_results.get('White', np.nan),
            'black_win_%': winning_results.get('Black', np.nan),
            'black_draw_%': draw_results.get('Black', np.nan),
            'white_games': total_games.get('White', np.nan),
            'black_games': total_games.get('Black', np.nan),
        })

    # Zapis wyników do pliku CSV
    results_df = pd.DataFrame(results_list)
    results_df.to_csv(f'chess_development_advantage_results_{development_lead}.csv', index=False)