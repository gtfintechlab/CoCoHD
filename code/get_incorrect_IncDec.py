import pandas as pd

save_path = '../data/analysis_data/IncDec_incorrect.xlsx'

inc_dec_true_path = '../data/raw_data/inc_dec_classifier_labeled_data_701.csv'
inc_dec_pred_path = '../data/analysis_data/IncDec_results.csv'

inc_dec_true = pd.read_csv(inc_dec_true_path)
inc_dec_pred = pd.read_csv(inc_dec_pred_path)

inc_dec_true.columns = ['id', 'sentence', 'label']
inc_dec_pred.columns = ['id', 'sentence', 'label']

inc_dec_pred = inc_dec_pred.sort_values(by='id').reset_index(drop=True)

inc_dec_merged = pd.merge(inc_dec_true, inc_dec_pred, on='id')
inc_dec_incorrect = inc_dec_merged[inc_dec_merged['label_x'] != inc_dec_merged['label_y']].drop(columns=['sentence_y'])
inc_dec_incorrect.columns = ['id', 'sentence', 'true_label', 'pred_label']

print(inc_dec_incorrect.head())

inc_dec_incorrect.to_excel(save_path, sheet_name='Sheet1', index=False)
print(f'DataFrame saved to {save_path}')
