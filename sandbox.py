import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    data = pd.read_csv('clean_job_data.csv')
    # Number of job posting per classification
    subset1 = data.copy().groupby(["FIELD"]).count().sort_values(["SUB-FIELD"], ascending=False).reset_index()[['FIELD', 'SUB-FIELD']]
    print(subset1)
    # Mean number of words per ad grouped by classification
    data['WORD-COUNT'] = data['DESCRIPTION'].apply(lambda x: len(str(x).split()))
    subset2 = data.copy().groupby(['FIELD'])['WORD-COUNT'].mean()
    print(subset2)
    # Boxplot number of words
    subset3 = data[['FIELD', 'WORD-COUNT']].groupby(['FIELD'])
    subset3.boxplot(subplots=False, rot=45, fontsize=12)
    plt.show()
