from pymongo import MongoClient
import ssl

import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
from gensim import corpora, models
import uuid

import os

nltk.download('wordnet')

def generate_new_topics(learning_objects):
    client = MongoClient(os.environ.get('MONGODB_CONNECTION'), ssl_cert_reqs=ssl.CERT_NONE)
    learning_objects_collection = client.onion.objects
    users_collection = client.onion.users
    released_learning_objects = list(learning_objects_collection.find({ 'status': 'released' }))

    learning_object_descriptions = []
    for released_learning_object in released_learning_objects:
        learning_object_description = released_learning_object.get('description')
        if learning_object_description is not None:
            learning_object_descriptions.append(learning_object_description)

    processed_docs = []
    for learning_object_description in learning_object_descriptions:
        processed_doc = preprocess(learning_object_description)
        processed_docs.append(processed_doc)

    dictionary = gensim.corpora.Dictionary(processed_docs)
    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

    tfidf = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf[bow_corpus]

    lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=20, id2word=dictionary, passes=20, workers=4)

    corpus = lda_model_tfidf[corpus_tfidf]

    topic_id_dict = {}
    for i, bow_item in enumerate(bow_corpus):

        topic_dist = lda_model_tfidf.get_document_topics(bow_item)
        
        max_prob = 0
        id_for_max = 0
        for topic_prob in topic_dist:
            if max_prob < topic_prob[1]:
                max_prob = topic_prob[1]
                id_for_max = topic_prob[0]
                
        if id_for_max in topic_id_dict:
            topic_id_dict[id_for_max].append(learning_object_descriptions[i])
        else:
            topic_id_dict[id_for_max] = [learning_object_descriptions[i]]

    
    topic_to_cuid_dict = {}

    for key in topic_id_dict:
        for learning_object_description in topic_id_dict.get(key):
            for learning_object in released_learning_objects:
                if (learning_object_description == learning_object.get('description')):
                    author = users_collection.find_one({ '_id': learning_object.get('authorID') }, { '_id': 0, 'email': 1, 'name': 1, 'organization': 1, 'username': 1 })
                    learning_object['author'] = author
                    if key in topic_to_cuid_dict:
                        topic_to_cuid_dict[key].append(learning_object)
                    else:
                        topic_to_cuid_dict[key] = [learning_object]

    out = {}
    for index, topic in enumerate(topic_to_cuid_dict):
        for learning_object in topic_to_cuid_dict.get(topic):
            for given_learning_object in learning_objects:
                if given_learning_object.get('learning_object').get('cuid') == learning_object.get('cuid'):
                    topic_name = str(uuid.uuid4())
                    if topic_name in out:
                        out[topic_name].append(learning_object)
                    else:
                        out[topic_name] = [learning_object]
    return out

def lemmatize_stemming(text):
    np.random.seed(2020)
    stemmer = SnowballStemmer('english')
    
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result