import Analyzer
import time
import sys
from multiprocessing import freeze_support, cpu_count

import CastlingAnalyzer
from data.processing.BasicStatsGetter import BasicStatsGetter
from data.processing.DataPreparator import DataPreparator

data_paths = [
    "./data/sub_elite_data.csv",
    "./data/elite_data.csv",
    "./data/TCEC_data.csv"
]

# DO NOT COMMENT OR REMOVE 2 LINES BELOW, NOTHING WILL WORK WITHOUT THEM
# EVEN IF YOU DON'T PLAN ON USING ANY THREADING
if __name__ == '__main__':
    freeze_support()  # needed for threading

    # -------------
    # CODE HERE
    # ------------

    # GET BASIC STATS
    # bsg = BasicStatsGetter()
    # bsg.draw_elo_histogram(data_paths[0], "sub-elitarnych", "#94ddbc")
    # bsg.draw_elo_histogram(data_paths[1], "elitarnych", "#f9a03f")
    # bsg.draw_elo_histogram(data_paths[2], "silników szachowych", "#d782ba")

    # PREPARE DATA
    # dp = DataPreparator("./data/elite_data.csv", "./data/elite_data_split.csv")
    # dp.split_into_files(4)

    # ANALISIS CODE
    skiping_first = 0
    n_cores = cpu_count()  # number of logical cores on the machine
    analyzer = Analyzer.Analyzer("./results/center_control/empirical/results_elite_joined.csv", "./results/center_control/empirical/results_elite_final.csv",
                                 amount_of_workers=n_cores,
                                 amount_to_analise=100
                                 )
    print(f"Starting analysis...")
    start_time = time.time()
    analyzer.run_analysis(skip_first=skiping_first,save_interval=10)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Analysis completed in {execution_time:.3f} seconds.")
    sys.exit(0)

    # ca = CastlingAnalyzer.CastlingAnalyzer(0)
    # ca.analyze_empirical_results("./results/castling/empirical/results_sub_elite_joined.csv", "./check.csv")
