# Package for getting local time
import time

# Package for data wrangling
import pandas as pd

# Package for system path traversal
import os

# Package for working with dates
from datetime import date

# Import the main analysis pipeline
from pipeline import Pipeline

# Tensor creation class
from text_preprocessing import TextToTensor

# Reading the configuration file
import yaml

with open("conf.yml", 'r') as file:
    conf = yaml.safe_load(file).get('pipeline')

# Chunker
from text_chunker import Chunker

# Reading the stop words
stop_words = []
try:
    stop_words = pd.read_csv('data/stop_words.txt', sep='\n', header=None)[0].tolist()
except Exception as e:
    # This exception indicates that the file is missing or is in a bad format
    print('Bad stop_words.txt file: {e}')

# Reading the data
train = pd.read_csv('data/train.csv')[['TEXT', 'TARGET']]

# Shuffling the data for the k fold analysis
train = train.sample(frac=1)

# Creating the input for the pipeline
X_train = train['TEXT'].astype(str).tolist()
Y_train = train['TARGET'].tolist()

start_time = time.time()
print('=' * 200)
print('Running the RNN pipeline')
print('-' * 200)
print()
# Running the pipeline with all the data
RNN = Pipeline(
    X_train=X_train,
    Y_train=Y_train,
    embed_path='embeddings\\glove.840B.300d.txt',
    embed_dim=300,
    stop_words=stop_words,
    max_len=conf.get('max_len'),
    epochs=conf.get('epochs'),
    batch_size=conf.get('batch_size')
)
RNN.model.summary();
print()
print(f'Finished in {time.time() - start_time}s')

job_data = pd.read_csv('data/clean_job_data.csv').iloc[:, :]

TextToTensor_instance = TextToTensor(
        tokenizer=RNN.tokenizer,
        max_len=conf.get('max_len')
    )

TextChunker_instance = Chunker(
        grammar=r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""
    )

for index, row in job_data.iterrows():
    job_desc = row['DESCRIPTION']
    # job_desc = row['TEXT']

    chunks = TextChunker_instance.get_continuous_chunks(job_desc)
    skills = []
    for chunk in chunks:
        chunk_nn = TextToTensor_instance.string_to_tensor([" ".join(chunk)])
        p_chunk = RNN.model.predict(chunk_nn)[0][0]
        if p_chunk > 0.5:
            skills.append(" ".join(chunk))
        # print(f'Sentence: "{" ".join(chunk)}" Score: {p_chunk}')
    print('-' * 200)
    print(f'Job title: "{row["TITLE"]}" \nSkills: {skills}')
    print('-' * 200)
    job_data.loc[index, 'skills'] = ','.join(skills)

# Saving the predictions to a csv file
if conf.get('save_results'):
    if not os.path.isdir('output'):
        os.mkdir('output')

    job_data.to_csv(
        f'output/submission_{date.today()}_{time.strftime("%H-%M-%S", time.localtime())}.csv', index=False)


# # Some sanity checks
# good = ["maths skills"]
# bad = ["some mouldy athletes on your plate"]
#
# TextToTensor_instance = TextToTensor(
#     tokenizer=RNN.tokenizer,
#     max_len=conf.get('max_len')
# )
#
# # Converting to tensors
# good_nn = TextToTensor_instance.string_to_tensor(good)
# bad_nn = TextToTensor_instance.string_to_tensor(bad)
#
# # Forecasting
# p_good = RNN.model.predict(good_nn)[0][0]
# p_bad = RNN.model.predict(bad_nn)[0][0]
#
# print(f'Sentence: {good_nn} Score: {p_good}')
# print(f'Sentence: {bad_nn} Score: {p_bad}')
#
# # Saving the predictions
# test['prob_is_genuine'] = results.yhat
# test['target'] = [1 if x > 0.2 else 0 for x in results.yhat]
#
# # Saving the predictions to a csv file
# if conf.get('save_results'):
#     if not os.path.isdir('output'):
#         os.mkdir('output')
#
#     test[['TEXT', 'target']].to_csv(
#         f'output/submission_{date.today()}_{time.strftime("%H-%M-%S", time.localtime())}.csv', index=False)
