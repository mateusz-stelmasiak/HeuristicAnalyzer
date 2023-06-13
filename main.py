import CastlingAnalyzer
import DevelopingAnalyzer
from QueenDevelopmentAnalyzer import QueenDevelopmentAnalyzer
import data.PGNtoCSVParser
from data.BasicStatsGetter import BasicStatsGetter

# DATA
#parser = data.PGNtoCSVParser.PGNtoCSVParser("./data/lichess_standard_1.csv")
#parser.parse_all_in_folder("./data/lichess_standard_raw",max_elo_diff=300, max_elo=2300)

bsg = BasicStatsGetter()
bsg.get_basic_stats("./data/lichess_standard_1.csv")

# HEURISTIC: Castle soon
# castling_analyzer = CastlingAnalyzer.CastlingAnalyzer(data_file_path)
# castling_analyzer.calculate_castling_turns()
# castling_analyzer.calculate_win_rates()
# #castling_analyzer.calculate_castling_effectiveness()
# castling_analyzer.analyse_castling_data()

# HEURISTIC: Control the center
# center_anal = CenterAnalyzer.CenterAnalyzer(data_file_path)
# center_anal.analyze_center()
# center_anal.create_plot("center_analysis.csv")

# HEURISTIC: Don't develop the queen early
# analyzer = QueenDevelopmentAnalyzer(data_file_path)
# analyzer.analyze_queen_development()


# DEVELOP PIECES BEFORE PAWNS

#developing_analyzer = DevelopingAnalyzer.DevelopingAnalyzer(data_file_path)
#developing_analyzer.print_data()

