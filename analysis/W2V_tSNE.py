import gensim 
import pandas as pd
import numpy
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


cleaneddoc = pd.read_pickle('cleaned_doc.txt')
model = gensim.models.Word2Vec(cleaneddoc, size=200, window=6, min_count=5, workers=1)

vocabulary = sorted(model.vocab)
emb_tuple = tuple([model[v] for v in vocabulary])
X = numpy.vstack(emb_tuple)
X_embedded = TSNE(n_components=2, perplexity=40, verbose=2).fit_transform(X)


fig, ax = plt.subplots()
ax.scatter(X_embedded[:, 0], X_embedded[:, 1])
for i, txt in enumerate(vocabulary):
    ax.annotate(txt, (X_embedded[i, 0],X_embedded[i, 1]))
plt.show()
