import pandas as pd
import time
import nltk
from collections import OrderedDict
import numpy as np
import re

stopwords = nltk.corpus.stopwords.words('english')


class TextRank4Keyword():
    """
    Extract keywords from text
    """
    def __init__(self):
        self.d = 0.85  # damping coefficient, usually is .85
        self.min_diff = 1e-5  # convergence threshold
        self.steps = 10  # iteration steps
        self.node_weight = None  # save keywords and its weight

    def sentence_segment(self, doc, allowed_pos, lower):
        sentences = []
        for sent in doc.split('.'):
            tokens = nltk.word_tokenize(sent)
            tags = nltk.pos_tag(tokens)
            tag_words = []
            for pos_tag in allowed_pos:
                if lower:
                    tag_words = tag_words + [t[0].lower() for t in tags if (t[1] == pos_tag and t[0] not in stopwords)]
                else:
                    tag_words = tag_words + [t[0] for t in tags if (t[1] == pos_tag and t[0] not in stopwords)]

            if tag_words:
                sentences.append(tag_words)
        return sentences

    def get_vocab(self, sentences):
        """Get all tokens"""
        vocab = OrderedDict()
        i = 0
        for sentence in sentences:
            for word in sentence:
                if word not in vocab:
                    vocab[word] = i
                    i += 1
        return vocab

    def get_token_pairs(self, window_size, sentences):
        """Build token_pairs from windows in sentences"""
        token_pairs = list()
        for sentence in sentences:
            for i, word in enumerate(sentence):
                for j in range(i + 1, i + window_size):
                    if j >= len(sentence):
                        break
                    pair = (word, sentence[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs

    def symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())

    def get_matrix(self, vocab, token_pairs):
        """Get normalized matrix"""
        # Build matrix
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')
        for word1, word2 in token_pairs:
            i, j = vocab[word1], vocab[word2]
            g[i][j] = 1
        # Get Symmetric matrix
        g = self.symmetrize(g)
        # Normalize matrix by column
        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm != 0)  # this is ignore the 0 element in norm
        return g_norm

    def get_keywords(self, number=10):
        """Print top number keywords"""
        node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
        keys = []
        for i, (key, value) in enumerate(node_weight.items()):
            # print(key + ' - ' + str(value))
            keys.append(key)
            if i > number:
                break
        return keys

    def analyze(self, text,
                allowed_pos=['NN', 'NNP', 'VB'],
                window_size=4, lower=False):
        """Main function to analyze text"""

        # Filter sentences
        sentences = self.sentence_segment(text, allowed_pos, lower)  # list of list of words

        # Build vocabulary
        vocab = self.get_vocab(sentences)

        # Get token_pairs from windows
        token_pairs = self.get_token_pairs(window_size, sentences)

        # Get normalized matrix
        g = self.get_matrix(vocab, token_pairs)

        # Initionlization for weight(pagerank value)
        pr = np.array([1] * len(vocab))

        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr = (1 - self.d) + self.d * np.dot(g, pr)
            if abs(previous_pr - sum(pr)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weight = dict()
        for word, index in vocab.items():
            node_weight[word] = pr[index]

        self.node_weight = node_weight


if __name__ == '__main__':
    print("Loading dataset...")
    t0 = time.time()
    data = pd.read_csv('clean_job_data.csv')
    print("Done in %0.3fs" % (time.time() - t0))

    for index, row in data.iterrows():
        text = re.sub('[^a-z0-9 ]', '', row.DESCRIPTION)
        tr4w = TextRank4Keyword()
        tr4w.analyze(text, allowed_pos=['NN', 'NNP', 'VB'], window_size=4, lower=False)
        print('"{}" in {} - {}'.format(row.TITLE.strip(), row.FIELD, row['SUB-FIELD']))
        keywords = tr4w.get_keywords(20)
        data.loc[index, 'KEYWORDS'] = ', '.join(keywords)
        print(keywords)
    data.to_csv('keywords.csv', index=False, encoding='utf-8-sig')
