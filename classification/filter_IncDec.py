import pandas as pd

relevancy_results_file_path = '../data/hearing_data/classification_data/relevancy_full_labeled.csv'
IncDec_full_results_save_path = '../data/hearing_data/classification_data/IncDec_full_unlabeled.csv'

relevancy_results = pd.read_csv(relevancy_results_file_path)

IncDec_only = relevancy_results[relevancy_results['label'] != 'i']
IncDec_only = IncDec_only.sort_values(by='id').reset_index(drop=True)
IncDec_only = IncDec_only.drop(columns=['label'])

IncDec_only.to_csv(IncDec_full_results_save_path, index=False)
print("IncDec_full_unlabeled saved to a csv in the current folder.")