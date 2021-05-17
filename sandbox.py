import pandas as pd
import matplotlib.pyplot as plt
import nltk
import time

if __name__ == '__main__':
    # data = pd.read_csv('clean_job_data.csv')
    # # Number of job posting per classification
    # subset1 = data.copy().groupby(["FIELD"]).count().sort_values(["SUB-FIELD"], ascending=False).reset_index()[['FIELD', 'SUB-FIELD']]
    # print(subset1)
    # # Mean number of words per ad grouped by classification
    # data['WORD-COUNT'] = data['DESCRIPTION'].apply(lambda x: len(str(x).split()))
    # subset2 = data.copy().groupby(['FIELD'])['WORD-COUNT'].mean()
    # print(subset2)
    # # Boxplot number of words
    # subset3 = data[['FIELD', 'WORD-COUNT']].groupby(['FIELD'])
    # subset3.boxplot(subplots=False, rot=45, fontsize=12)
    # plt.show()
    data = pd.read_csv('clean_job_data.csv')

    # Get first job posting per FIELD
    dat = data.groupby('FIELD').first().reset_index().iloc[0:10, :]
    # print(dat)

    for index, row in dat.iloc[0:1, :].iterrows():
        text = row['DESCRIPTION']
        # print(text)
        tokens = nltk.word_tokenize(text)
        # print(tokens)
        tags = nltk.pos_tag(tokens)
        # print(tags)
        grammar = "NP: {<DT>?<JJ>*<NN>}"
        # cp = nltk.RegexpParser(grammar)
        # result = cp.parse(tags)
        # print(result)
        # result.draw()
        print('Job: {}'.format(row['TITLE']))

        do_list = []
        experience_list = []
        for i in range(len(tags)):
            if tags[i][1] == "NN":
                try:
                    if tags[i + 1][1] == "NNS" or tags[i + 1][1] == "NN":
                        do_list.append("{} {}".format(tags[i][0], tags[i + 1][0]))
                except IndexError:
                    pass
            if tags[i][1] == "VBG":
                try:
                    if tags[i + 1][1] == "NNS" or tags[i + 1][1] == "NN":
                        experience_list.append("{} {}".format(tags[i][0], tags[i + 1][0]))
                except IndexError:
                    pass
        print('Description: ')
        print(row['DESCRIPTION'])
        print('Tags: ')
        print(tags)
        print('What you\'ll do: ')
        print(do_list)

        nnp_tags = [t[0] for t in tags if t[1] == "NNP"]
        experience_list.append(nnp_tags)
        print('Skills required: ')
        print(experience_list)
        print('-' * 200)


# JJ -> NN
# JJ -> NNS
# NN
#
#
# managing budgets
#
# marketing experience
