import csv

import nltk
import pandas as pd
import matplotlib.pyplot as plt
import time
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk import RegexpParser
from nltk import Tree

# Defining a grammar & Parser
NP = "NP: {(<V\w+>|<NN\w?>)+.*<NN\w?>}"
chunker = RegexpParser(NP)


def get_continuous_chunks(text, chunk_func=ne_chunk):
    chunked = chunk_func(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == Tree:
            current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    return continuous_chunk


if __name__ == '__main__':
    data = pd.read_csv('clean_job_data.csv')
    # Get first job posting per FIELD
    dat = data.groupby('FIELD').first().reset_index().iloc[:, :]
    # print(dat)

    with open('noun_phrases.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PHRASE', 'IS_SKILL'])

    for index, row in dat.iterrows():
        txt = row['DESCRIPTION']
        chunks = get_continuous_chunks(txt, chunker.parse)
        with open('noun_phrases.csv', 'a') as csvfile:
            for noun_phrase in chunks:
                csvfile.write(noun_phrase + '\n')
        print(chunks)
