from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig, pipeline
from transformers.pipelines.pt_utils import KeyDataset
from datasets import load_dataset
from tqdm.auto import tqdm
import time
import csv
import os

from concurrent.futures import ThreadPoolExecutor

path = "../binary_model"
results_path = '../data/analysis_data/relevancy_results.csv'

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

# Alternative
dataset = load_dataset('csv', data_files="../data/raw_data/filtered_sentences_full.csv", split='train')
# dataset = load_dataset('csv', data_files="../data/raw_data/classification_test_data.csv", split='train')

tokenizer = AutoTokenizer.from_pretrained(path, do_lower_case=True, do_basic_tokenize=True)
model = AutoModelForSequenceClassification.from_pretrained(path, num_labels=2)
config = AutoConfig.from_pretrained(path)

classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, device=0, framework="pt")

def classify(row):
    id, date, hearing_num, sentence = row['Unnamed: 0'], row['date'], row['hearing_num'], row['sentences']
    label_dict = {'LABEL_0': "i", "LABEL_1": 'r'}
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
    executor.map(classify, dataset)














# def data():
#     with open('../data/raw_data/filtered_sentences_full.csv', 'r') as csvfile:
#         csv_reader = csv.reader(csvfile)
#         for row in csv_reader:
#             yield row

# cnt = 0
# for id, date, hearing_num, sentence in tqdm(data()):
#     if cnt == 20:
#         break
#     label_dict = {'LABEL_0': "i", "LABEL_1": 'r'}
#     label = label_dict[classifier(sentence, batch_size=4, truncation='only_first', max_length=512)[0]['label']]
#     # print(f"{id}, {date}, {hearing_num}, {sentence}, {label}")
#     cnt += 1


# Alternative
# for out in KeyDataset(dataset, 'sentences'):
# cnt = 0
# for out in dataset:
#     if cnt == 20:
#         break

#     id, date, hearing_num, sentence = out['Unnamed: 0'], out['date'], out['hearing_num'], out['sentences']

    # label_dict = {'LABEL_0': "i", "LABEL_1": 'r'}
    # label = label_dict[classifier(sentence, batch_size=4, truncation='only_first', max_length=512)[0]['label']]

#     print(f"{id}, {date}, {hearing_num}, {sentence}, {label}")

#     cnt += 1