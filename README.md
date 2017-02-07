# Insight Data Science Fellowship Project
http://insightdatascience.com/
# 
[RoadMap: Personalized online courses towards a data science career](https://www.datascienceroadmap.com)

### Install

This project requires **Python 2.7** and the following Python libraries installed:

- [Flask](http://flask.pocoo.org/)
- [sqlalchemy](http://www.sqlalchemy.org/) 
- [scikit-learn](http://scikit-learn.org/stable/)
- [Gensim](https://radimrehurek.com/gensim/)
- [NLTK](http://www.nltk.org/)
- [PDFMiner](https://euske.github.io/pdfminer/)
- [psycopg2](https://pypi.python.org/pypi/psycopg2)
- [Virtualenv](https://virtualenv.pypa.io/en/stable/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)


### The pipeline

<img src="/doc/pipeline.png">
The pipeline of the application.

I collected over 5,000 job postings and 4,000 online course data through Python’s beautiful soup web 
scraping library and API calls. I then processed the job descriptions using natural language processing. 
Where, I tokenized and stemmed the job descriptions and removed stopwords. Then, filtered the words based 
on their TF-IDF transformation. I stored the courses data in a PostgreSQL database.
Using gensim, I trained a word2vec model on all the preprocessed job descriptions, where a neural network 
is used to represent all the words into a word vector space.
I then wrote an algorithm which then takes a user’s uploaded resume and infers the missing skills. 

These missing skills were then ranked  based on two separate metrics. The first metric is the term frequency 
of the skill, which is a proxy for the market demand, and the second metric is based on the word cosine 
similarity in the pretrained word2vec model, in which I try to recommend new and unique skills from the 
users’ current skill set.
Finally, I provide the course recommendations using SQL queries based on the missing skills ranking.









### Future work

For the future work, I plan to run Latent Dirichlet Allocation (LDA) in order to extract topics from
the job postings directly which can be leveraged to provide personalized course recommendation based
on current job market for all job titles. Here, I provide an example of LDA on current data science
job postings.

<img src="/doc/lda.png">
LDA on current data science job postings.
