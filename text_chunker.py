from nltk import word_tokenize, RegexpParser
import nltk
from nltk.corpus import stopwords


def leaves(tree):
    """
    Finds NP (nounphrase) leaf nodes of a chunk tree.
    """
    for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
        yield subtree.leaves()


def get_terms(tree):
    for leaf in leaves(tree):
        term = [w.lower() for w, t in leaf]
        yield term


class Chunker:
    def __init__(self, grammar):
        self.chunker = RegexpParser(grammar)
        self.stopwords = stopwords.words('english')

    def get_continuous_chunks(self, text):
        """
        A method to get a list of continuous phrases in a text
        """
        toks = word_tokenize(text)
        postoks = nltk.tag.pos_tag(toks)
        tree = self.chunker.parse(postoks)
        return [term for term in get_terms(tree)]
