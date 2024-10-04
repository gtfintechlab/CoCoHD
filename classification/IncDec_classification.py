import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datasets import load_dataset
from tqdm.auto import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig, pipeline
# from transformers.pipelines.pt_utils import KeyDataset

def classify_IncDec():
    # Put the finetuned model under this path
    path = "../data/models/IncDec_final_model_roberta"

    # Check if the file exists
    if os.path.exists(results_path):
        # Ask the user whether to delete the existing file
        user_response = input(f"The file '{results_path}' already exists. Do you want to delete it? (y/n): ").lower()

        if user_response == 'y':
            # Delete the existing file
            os.remove(results_path)
            print(f"Existing file '{results_path}' deleted.")
        elif user_response == 'n':
            print("File not deleted. Exiting the program.")
            exit()
        else:
            print("Invalid input. Please enter 'y' or 'n'. Exiting the program.")
            exit()

    with open(results_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'date', 'hearing_num', 'sentence', 'label']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header
        csv_writer.writeheader()

    dataset = load_dataset('csv', data_files="../data/classification_data/IncDec_full_unlabeled.csv", split='train')

    tokenizer = AutoTokenizer.from_pretrained(path, do_lower_case=True, do_basic_tokenize=True)
    model = AutoModelForSequenceClassification.from_pretrained(path, num_labels=3)
    config = AutoConfig.from_pretrained(path)

    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, device=0, framework="pt")

    def classify_row(row):
        id, date, hearing_num, sentence = row['id'], row['date'], row['hearing_num'], row['sentence']
        label_dict = {'LABEL_0': "p", "LABEL_1": 'd', "LABEL_2": "n"}
        label = label_dict[classifier(sentence, batch_size=4, truncation='only_first', max_length=512)[0]['label']]

        with open(results_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'hearing_num', 'sentence', 'label']
            writer = csv.DictWriter(csvfile, fieldnames)

            # Write the result for the current text
            writer.writerow({
                'id': id,
                'date': date,
                'hearing_num': hearing_num,
                'sentence': sentence,
                'label': label
            })

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        executor.map(classify_row, dataset)

if __name__ == "__main__":
    results_path = '../data/classification_data/IncDec_full_labeled.csv'
    classify_IncDec()