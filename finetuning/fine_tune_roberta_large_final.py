from fine_tune_plm_grid_search import fine_tune_plm

save_model_path = "../model_data/IncDec_final_model_roberta"

seed = 944601
language_model_to_use = "roberta-large"
data_category = "IncDec"
train_data_path = "../data/train/" + data_category + "-train-" + str(seed) + ".xlsx"
test_data_path = "../data/test/" + data_category + "-test-" + str(seed) + ".xlsx"
output = fine_tune_plm(gpu_numbers="0", 
                       train_data_path=train_data_path, 
                       test_data_path=test_data_path,
                       language_model_to_use=language_model_to_use, 
                       seed=944601, 
                       batch_size=32, 
                       learning_rate=1e-5, 
                       save_model_path=save_model_path,
                       num_labels=3)
print(output)