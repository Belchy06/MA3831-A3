import pandas as pd
import re


def preprocess_data(data):
    for column in data:
        data[column] = [re.sub("[\"']", '', elem.lower()) for elem in data[column].tolist()]
        data[column] = [elem.replace("\n", " ") for elem in data[column].tolist()]
        data[column] = [re.sub(r'\s+', ' ', elem) for elem in data[column].tolist()]
        data[column] = [elem.replace(u'\ufffd', '') for elem in data[column].tolist()]
    return data


def rename_job_columns(data):
    data['FIELD'] = [re.sub("[-]", ' ', elem.lower()) for elem in data['FIELD'].tolist()]
    data['FIELD'] = [re.sub("(?:jobs in )", '', elem.lower()) for elem in data['FIELD'].tolist()]
    data['SUB-FIELD'] = [re.sub("[-]", ' ', elem.lower()) for elem in data['SUB-FIELD'].tolist()]
    data['TITLE'] = [re.sub('(?:- seek)', '', elem) for elem in data['TITLE'].tolist()]
    return data


if __name__ == '__main__':
    dataset = pd.read_csv('job_data.csv')
    dataset = preprocess_data(dataset.copy())
    dataset = rename_job_columns(dataset.copy())
    dataset.to_csv("clean_job_data.csv", index=False, encoding='utf-8-sig')
