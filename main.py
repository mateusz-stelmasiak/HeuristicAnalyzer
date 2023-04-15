from QueenDevelopmentAnalyzer import QueenDevelopmentAnalyzer

# DATA
data_file_path = "./data/chess_com_data.csv"
# chess_com_data_downloader = ChessDotComDataDownloader.ChessDotComDataDownloader(data_file_path)
# chess_com_data_downloader.download_data_by_title('GM')

# HEURISTIC: Castle soon
# castling_analyzer = CastlingAnalyzer.CastlingAnalyzer(data_file_path)
# #castling_analyzer.calculate_castling_vars()
# #castling_analyzer.calculate_win_rates()
# #castling_analyzer.calculate_castling_effectiveness()
# castling_analyzer.analyse_castling_data()

# HEURISTIC: Control the center
# center_anal = CenterAnalyzer.CenterAnalyzer(data_file_path)
# center_anal.analyze_center()
# center_anal.create_plot("center_analysis.csv")

# HEURISTIC: Don't develop the queen early
analyzer = QueenDevelopmentAnalyzer(data_file_path)
analyzer.analyze_queen_development()

