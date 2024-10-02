import numpy as np
import csv
import os
import requests

from gensim.models import KeyedVectors

url = "https://media.githubusercontent.com/media/eyaler/word2vec-slim/master/GoogleNews-vectors-negative300-SLIM.bin.gz"
filename = "GoogleNews-vectors-negative300-SLIM.bin.gz"

if not os.path.isfile(filename):
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download from {url}, status code: {response.status_code}")
else:
    print(f"{filename} already exists in the folder. Skipping download.")

model = KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300-SLIM.bin.gz', binary=True)

def get_top_similar_tokens(words, topn):
    combined_similar_words_set = set([])
    for w in words:
        most_similar_words = model.most_similar(w, topn=topn)
        # for most_similar_word in most_similar_words:
        #     combined_similar_words_set.add(most_similar_word[0].lower())
        combined_similar_words_set = combined_similar_words_set | set([word for word, _ in model.most_similar(w, topn=topn)])
        
    combined_similar_words_with_score = []
    for similar_word in combined_similar_words_set:
        combined_similarity_score = 0
        for word in words:
            sim_score = model.similarity(word, similar_word)
            combined_similarity_score = combined_similarity_score + sim_score
        combined_similar_words_with_score.append((similar_word, combined_similarity_score))

    combined_similar_words_with_score.sort(key=lambda x: x[1], reverse=True)

    # top_similar_tokens = set([word.lower() for word, score in combined_similar_words_with_score])

    return combined_similar_words_with_score

words = ['clean', 'energy', 'fuel', 'fossil', 'renewable', 'gas', 'decarbonize', 'unrenewable', 'drilling']
# words = ['clean', 'energy']
top_similar_tokens = get_top_similar_tokens(words, 100)

target_words = set([])
for token, _ in top_similar_tokens:
    if len(target_words) == 100:
        break
    target_words.add(token.lower())
target_words

with open('../data/target_word_list.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    for row in list(target_words):
        csvwriter.writerow([row])