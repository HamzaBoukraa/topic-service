import joblib
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import re
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from statistics import mean

nltk.download('stopwords')

MAX_VOCAB_SIZE = 20000
MAX_SEQUENCE_LENGTH = 100

# Model Path Constants
bidirectional_rnn_classification_model_path = './models/bidirectional_rnn_classifier.sav'
cnn_classification_model_path               = './models/cnn_classifier.sav'
rnn_classification_model_path               = './models/rnn_classifier.sav'

# Loaded Model Constants
bidirectional_rnn_classification_model = joblib.load(bidirectional_rnn_classification_model_path)
bidirectional_rnn_classification_model._make_predict_function()

cnn_classification_model = joblib.load(cnn_classification_model_path)
cnn_classification_model._make_predict_function()

rnn_classification_model = joblib.load(rnn_classification_model_path)
rnn_classification_model._make_predict_function()

available_models = [bidirectional_rnn_classification_model, cnn_classification_model, rnn_classification_model]

# Iterates over an array of Learning Objects
# and determines the best exisiting topic
# for each. Learning Objects that do not
# belong to any existing topic are grouped
# together in the dictionary output
def determine_learning_object_placements(learning_objects):

    output = {}

    for learning_object in learning_objects:

        confidence_score_sets = get_topic_confidence_scores(learning_object)

        highest_scores = {}
        
        for set_number in confidence_score_sets:

            # Find the index of the highest confidence score
            confidence_scores = confidence_score_sets.get(set_number)[0]

            highest_confidence_score = 0
            highest_confidence_score_index = 0
            for index, confidence_score in enumerate(confidence_scores):

                score_as_percent = confidence_score * 100
                if score_as_percent > highest_confidence_score:
                    highest_confidence_score = score_as_percent
                    highest_confidence_score_index = index

            highest_scores[set_number] = { 'score_as_percent': highest_confidence_score, 'index': highest_confidence_score_index }

        # Count the number of occurences
        # for each unique index
        # 
        # Record the most frequent index
        # and the number of occurrences for
        # that index
        index_count = {}
        for high_score in highest_scores:
            if highest_scores[high_score].get('index') in index_count:
                index_count[highest_scores[high_score].get('index')] += 1
            else:
                index_count[highest_scores[high_score].get('index')] = 1

        most_fequent_index = -1 
        highest_occurence_rate = 0
        for index in index_count:
            if index_count.get(index) > highest_occurence_rate:
                highest_occurence_rate = index_count.get(index)
                most_fequent_index = index
        
        most_frequent_scores = []
        for high_score in highest_scores:
            if highest_scores[high_score].get('index') == most_fequent_index:
                most_frequent_scores.append( highest_scores[high_score].get('score_as_percent'))

        # If highest_occurence_rate is less than or equal to 1,
        # set the topic id for this Learning Object to -1, indicating
        # that it belongs in its own topic
        print(highest_occurence_rate)
        print(most_frequent_scores)
        if highest_occurence_rate <= 1:
            most_fequent_index = -1
        # If the highest_occurence_rate is greater than 1,
        # calculate the average of confidence scores. If the
        # average is less than the desired theshold, set the
        # topic is for this Learning Object to -1, indicating
        # that is belongs in its own topic
        # 
        # If the average is greater than or equal to the desired
        # threshold, set the topic id to the standard index id,
        # indicating that this Learning Object belongs in the
        # standard topic
        else:
            avg = mean(most_frequent_scores)
            if avg < 20:
                most_fequent_index = -1

        output[learning_object.get('cuid')] = most_fequent_index
            
    return output

def get_topic_confidence_scores(learning_object):
    output = {}

    learning_object_description = clean_description(learning_object.get('description'))

    numeric_description = convert_description_to_prediction_format(learning_object_description)

    for index, model in enumerate(available_models):
        output[index] = model.predict(numeric_description)

    return output 

def convert_description_to_prediction_format(learning_object_description):
    learning_object_description = clean_description(learning_object_description)

    tokenizer = Tokenizer(num_words=MAX_VOCAB_SIZE)
    tokenizer.fit_on_texts([learning_object_description])
    sequences = tokenizer.texts_to_sequences([learning_object_description])
    data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    
    return data

def clean_description(learning_object_description):
    cleanr = re.compile('<.*?>')
    cleaned_description = re.sub(cleanr, '', learning_object_description)
    cleaned_description = re.sub('[^a-zA-Z]', ' ', learning_object_description)
    cleaned_description = cleaned_description.lower()
    cleaned_description = cleaned_description.split()

    ps = PorterStemmer()
    cleaned_description = [ps.stem(word) for word in cleaned_description if not word in set(stopwords.words('english')) and len(word) > 1]
    cleaned_description = ' '.join(cleaned_description)

    return cleaned_description