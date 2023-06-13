import Analyzer
import time

analyzer = Analyzer.Analyzer("./data/TCEC_data.csv", "./data/results.csv")
print(f"Starting analysis...")
start_time = time.time()
analyzer.run_analysis()
end_time = time.time()
execution_time = end_time - start_time
print(f"Analysis completed in {execution_time} seconds.")
