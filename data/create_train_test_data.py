import pandas as pd
from sklearn.model_selection import train_test_split

def encode(label_word):
    if label_word == "p":
        return 0
    elif label_word == "d":
        return 1
    elif label_word == "n":
        return 2
    
df = pd.read_csv("./raw_data/inc_dec_classifier_labeled_data_701.csv", usecols=['sentences', 'label'])

df["label"] = df["label"].apply(lambda x: encode(x))

for seed in [5768, 78516, 944601]: 
    print(f"Generating train and test datasets with random seed {seed}")
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=seed)
    train_df.to_excel(f'./train/IncDec-train-{seed}.xlsx', index=False)
    test_df.to_excel(f'./test/IncDec-test-{seed}.xlsx', index=False)
print("Dataset splitting is complete")