import pandas as pd

relevancy_results_file_path = 'relevancy_results.csv'

relevancy_results = pd.read_csv(relevancy_results_file_path)

IncDec_only = relevancy_results[relevancy_results['label'] != 'i']

print(IncDec_only.head())
print(len(IncDec_only))