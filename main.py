import Analyzer
import time
import sys
from multiprocessing import freeze_support, cpu_count

if __name__ == '__main__':
    freeze_support()  # needed for threading
    n_cores = cpu_count()  # number of logical cores on the machine
    analyzer = Analyzer.Analyzer("./data/lichess_standard.csv", "./results/results_standard.csv", 50, n_cores)
    print(f"Starting analysis...")
    start_time = time.time()
    analyzer.run_analysis()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Analysis completed in {execution_time:.3f} seconds.")
    sys.exit(0)
