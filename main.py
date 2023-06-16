import Analyzer
import time
import sys
from multiprocessing import freeze_support, cpu_count

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

    #GET BASIC STATS
    # bsg = BasicStatsGetter()
    # for path in data_paths:
    #     bsg.get_basic_stats(path)

    #PREPARE DATA
    # dp = DataPreparator("./data/elite_data.csv", "./data/elite_data_split.csv")
    # dp.split_into_files(4)
    
    # ANALISIS CODE
    n_cores = cpu_count()  # number of logical cores on the machine
    analyzer = Analyzer.Analyzer("data/elite_data.csv", "./results/results_elite.csv",
                                 amount_of_workers=n_cores)
    print(f"Starting analysis...")
    start_time = time.time()
    analyzer.run_analysis()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Analysis completed in {execution_time:.3f} seconds.")
    sys.exit(0)
