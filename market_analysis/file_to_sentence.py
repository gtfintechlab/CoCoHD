import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import subprocess
import nltk
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from datetime import datetime
from nltk.tokenize import sent_tokenize

df = pd.read_csv('/home/congress-user/data_collection/transcripts.csv')

# expanding transcripts into sentences
df['sentences'] = df['content'].astype(str).apply(sent_tokenize)
df['sentence_count'] = df['sentences'].str.len()
df = df[['date','hearing_num','sentences']]
df = df.explode('sentences').reset_index(drop=True)
df['sentences'] = df['sentences'].apply(lambda text:re.sub(r'[^a-zA-Z0-9\s]', '', text))
df['sentences'] = df['sentences'].str.replace('\n','')
df['tokens'] = df['sentences'].astype(str).apply(nltk.word_tokenize)

# df.to_csv('tokenized_sentences.csv')

# filter sentences base on keyword list
keyword_list = pd.read_csv('/home/congress-user/data_collection/EDA/word_list/word_list.csv',header=None)
keyword_list = keyword_list.rename(columns={0:'keyword'})

filtered_df = df.copy()
filtered_df = filtered_df[filtered_df['sentences'].str.lower().str.contains(fr"\b(?:{'|'.join(keyword_list['keyword'].values)})\b")]
filtered_df['sentences'] = filtered_df['sentences'].replace(r'\s+', ' ', regex=True)

filtered_df[['date','hearing_num','sentences']].to_csv('filtered_sentences_full.csv')