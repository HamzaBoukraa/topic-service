import joblib

# Model Path Constants
bidirectional_rnn_classification_model_path = './models/bidirectional_rnn_classifier.sav'
cnn_classification_model_path               = './models/cnn_classifier.sav'
rnn_classification_model_path               = './models/rnn_classifier.sav'

# Loaded Model Constants
bidirectional_rnn_classification_model = joblib.load(bidirectional_rnn_classification_model_path)
cnn_classification_model               = joblib.load(cnn_classification_model_path)
rnn_classification_model               = joblib.load(rnn_classification_model_path)

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
        for set_number, confidence_scores in enumerate(confidence_score_sets):
            # Find the index of the highest confidence score
            
            highest_confidence_score = 0
            highest_confidence_score_index = 0
            for index, confidence_score in enumerate(confidence_scores):
                if confidence_score > highest_confidence_score:
                    highest_confidence_score = confidence_score
                    highest_confidence_score_index = index
            
            # Store highest confidence score information
            # for each set of confidence scores
            highest_scores[set_number] = { 'score': highest_confidence_score, 'index': highest_confidence_score_index }

        
        for high_score in highest_scores:




def get_topic_confidence_scores(learning_object):
    output = {}

    for index, model in enumerate(available_models):
        output[index] = model.predict()

    return output 
