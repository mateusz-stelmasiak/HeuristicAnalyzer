import Analyzer

analyzer = Analyzer.Analyzer("./data/lichess_elite.csv", "./data/results_elite.csv", 10)
analyzer.run_analysis()
