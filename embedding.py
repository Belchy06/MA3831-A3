import pandas as pd

if __name__ == '__main__':
    data = pd.read_csv('noun_phrases.csv')
    data = data.iloc[0:800, :]

    X_train = []
    Y_train = []
    for index, row in data.iterrows():
        X_train.append(row['PHRASE'])
        is_skill = 1 if row['IS_SKILL'] == 'y' else 0
        Y_train.append(is_skill)

    print(Y_train)
