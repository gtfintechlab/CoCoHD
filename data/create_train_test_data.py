import pandas as pd
from sklearn.model_selection import train_test_split

def encode(label_word):
    if label_word == "i":
        return 0
    elif label_word == "r":
        return 1
    
df = pd.read_csv("./raw_data/relevancy_classifier_labeled_data.csv", usecols=['sentences', 'label'])

df["label"] = df["label"].apply(lambda x: encode(x))

for seed in [5768, 78516, 944601]: 
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=seed)
    train_df.to_excel(f'./train/relevancy-train-{seed}.xlsx', index=False)
    test_df.to_excel(f'./test/relevancy-test-{seed}.xlsx', index=False)