from time import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation


# n_samples = 2000
n_features = 1000
n_components = 10
n_top_words = 10


def plot_top_words(model, feature_names, n_top_words, title):
    fig, axes = plt.subplots(2, 5, figsize=(30, 15), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]

        ax = axes[topic_idx]
        topic_text = top_features[0]
        # top_features.pop(0)
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f'Topic {topic_idx +1} - {topic_text}',
                     fontdict={'fontsize': 15})
        ax.invert_yaxis()
        ax.tick_params(axis='both', which='major', labelsize=10)
        for i in 'top right left'.split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=20)

    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    plt.show()


if __name__ == '__main__':
    print("Loading dataset...")
    t0 = time()
    data = pd.read_csv('clean_job_data.csv')
    # data_samples = data[:n_samples][['DESCRIPTION']].DESCRIPTION.tolist()
    print("Done in %0.3fs" % (time() - t0))
    # Combine job postings per FIELD
    dat = data.groupby('FIELD')['DESCRIPTION'].apply(lambda x: ' '.join(x)).reset_index()
    group_lens = data.groupby('FIELD').count().reset_index()
    # print(dat)

    for index, field in dat.iterrows():
        # Use tf-idf features for NMF.
        n_samples = group_lens.iloc[index]['TITLE']
        data_samples = field.DESCRIPTION.split()
        # print(data_samples)
        # print("Extracting tf-idf features for NMF...")
        # tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
        #                                    max_features=n_features,
        #                                    stop_words='english')
        # t0 = time()
        # tfidf = tfidf_vectorizer.fit_transform(data_samples)
        # print("done in %0.3fs." % (time() - t0))

        # Use tf (raw term count) features for LDA.
        print("Extracting tf features for LDA...")
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                        max_features=n_features,
                                        stop_words='english')
        t0 = time()
        tf = tf_vectorizer.fit_transform(data_samples)
        print("done in %0.3fs." % (time() - t0))
        print()

        # # Fit the NMF model
        # print("Fitting the NMF model (Frobenius norm) with tf-idf features, "
        #       "n_samples=%d and n_features=%d..."
        #       % (n_samples, n_features))
        # t0 = time()
        # nmf = NMF(n_components=n_components, random_state=1,
        #           alpha=.1, l1_ratio=.5).fit(tfidf)
        # print("done in %0.3fs." % (time() - t0))
        #
        # tfidf_feature_names = tfidf_vectorizer.get_feature_names()
        # plot_top_words(nmf, tfidf_feature_names, n_top_words,
        #                'Topics in NMF model (Frobenius norm)')
        #
        # # Fit the NMF model
        # print('\n' * 2, "Fitting the NMF model (generalized Kullback-Leibler "
        #                 "divergence) with tf-idf features, n_samples=%d and n_features=%d..."
        #       % (n_samples, n_features))
        # t0 = time()
        # nmf = NMF(n_components=n_components, random_state=1,
        #           beta_loss='kullback-leibler', solver='mu', max_iter=1000, alpha=.1,
        #           l1_ratio=.5).fit(tfidf)
        # print("done in %0.3fs." % (time() - t0))
        #
        # tfidf_feature_names = tfidf_vectorizer.get_feature_names()
        # plot_top_words(nmf, tfidf_feature_names, n_top_words,
        #                'Topics in NMF model (generalized Kullback-Leibler divergence)')

        print('\n' * 2, "Fitting LDA models with tf features, "
                        "n_samples=%d and n_features=%d..."
              % (n_samples, n_features))
        lda = LatentDirichletAllocation(n_components=n_components, max_iter=5,
                                        learning_method='online',
                                        learning_offset=50.,
                                        random_state=0)
        t0 = time()
        lda.fit(tf)
        print("done in %0.3fs." % (time() - t0))

        tf_feature_names = tf_vectorizer.get_feature_names()
        plot_top_words(lda, tf_feature_names, n_top_words, 'Topics in LDA model - {}'.format(group_lens.iloc[index]['FIELD']))
        print()




