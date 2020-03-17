from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from elasticsearch_driver import get_learning_objects_without_topic
from classification_aggregator import determine_learning_object_placements
from new_topic_aggregator import generate_new_topics
from statistics import mode
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/')
@cross_origin()
def index():
    return jsonify({'message': 'Welcome to the Clark Topic Service'}), 200

@app.route('/topics/assign')
@cross_origin()
def predictTopicsForNewLearningObjects():
    # Finds all Learning Objects that do not have a topic
    learning_objects_without_topic = get_learning_objects_without_topic()

    # Determines which Learning Object belong in an existing topic
    # and which belong in a new topic
    predicted_learning_object_placements = determine_learning_object_placements(learning_objects_without_topic)

    new_topic_learning_objects = []
    standard_topic_learning_objects = {}
    
    for learning_object_cuid in predicted_learning_object_placements:
        if predicted_learning_object_placements.get(learning_object_cuid).get('topic_id') == -1:
            new_topic_learning_objects.append({'cuid': learning_object_cuid, 'version': predicted_learning_object_placements[learning_object_cuid].get('version'), 'name': predicted_learning_object_placements[learning_object_cuid].get('name'), 'author': predicted_learning_object_placements[learning_object_cuid].get('author') })
        else:
            if predicted_learning_object_placements.get(learning_object_cuid).get('topic_id') in standard_topic_learning_objects:
                standard_topic_learning_objects[predicted_learning_object_placements.get(learning_object_cuid).get('topic_id')].append({'cuid': learning_object_cuid, 'version': predicted_learning_object_placements[learning_object_cuid].get('version'), 'name': predicted_learning_object_placements[learning_object_cuid].get('name'), 'author': predicted_learning_object_placements[learning_object_cuid].get('author') })
            else:
                standard_topic_learning_objects[predicted_learning_object_placements.get(learning_object_cuid).get('topic_id')] = [{'cuid': learning_object_cuid, 'version': predicted_learning_object_placements[learning_object_cuid].get('version'), 'name': predicted_learning_object_placements[learning_object_cuid].get('name'), 'author': predicted_learning_object_placements[learning_object_cuid].get('author') }]

    new_topic_learning_objects = generate_new_topics(new_topic_learning_objects)

    # Each of these Learning Objects are then passed through
    # a cluster of classification models. Each model will return
    # an array probabilities, indicating a confidence that the
    # speficied Learning Object belongs in a topic.

    return jsonify({'standard_topics': standard_topic_learning_objects, 'new_topics': new_topic_learning_objects }), 200


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5001)