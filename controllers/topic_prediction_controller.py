from flask import jsonify, request
from services.elasticsearch_driver import get_learning_objects_without_topic, assign_topic_name
from services.mongodb_driver import get_all_topic_names, update_topic_name_list
from topic_identification.learning_object_classification import determine_learning_object_placements
from topic_identification.learning_object_clustering import generate_new_topics
from services.codebuild_driver import invoke_model_training_job
from controllers.auth import decode_authorization_jwt
from controllers.constants import HTTP_OK_CODE, HTTP_FORBIDDEN_CODE, HTTP_UNAUTHORIZED_CODE, HTTP_UNAUTHORIZED_MESSAGE, HTTP_FORBIDDEN_MESSAGE


def TopicPredictionController(app):

    @app.route('/topics/assign', methods=['GET'])
    def predictTopicsForNewLearningObjects():

        decoded_token = decode_authorization_jwt(request.headers.get( 'Authorization' ))

        if decoded_token is None:

            return jsonify({ 'message': HTTP_UNAUTHORIZED_MESSAGE }), HTTP_UNAUTHORIZED_CODE

        requester_access_groups = decoded_token.get('accessGroups')

        if requester_access_groups is None or 'admin' not in requester_access_groups and 'editor' not in requester_access_groups:

            return jsonify({ 'message': HTTP_FORBIDDEN_MESSAGE }), HTTP_FORBIDDEN_CODE

        topics = get_all_topic_names()
        
        # Finds all Learning Objects that do not have a topic
        learning_objects_without_topic = get_learning_objects_without_topic()

        # Determines which Learning Object belong in an existing topic
        # and which belong in a new topic
        predicted_learning_object_placements = determine_learning_object_placements(learning_objects_without_topic)

        new_topic_learning_objects = []
        standard_topic_learning_objects = {}
        
        for learning_object_cuid in predicted_learning_object_placements:
            if predicted_learning_object_placements.get(learning_object_cuid).get('topic_id') == -1:
                new_topic_learning_objects.append(predicted_learning_object_placements[learning_object_cuid])
            else:
                if predicted_learning_object_placements.get(learning_object_cuid).get('topic_id') in standard_topic_learning_objects:
                    standard_topic_learning_objects[topics[predicted_learning_object_placements.get(learning_object_cuid).get('topic_id')]].append(predicted_learning_object_placements[learning_object_cuid].get('learning_object'))
                else:
                    standard_topic_learning_objects[topics[predicted_learning_object_placements.get(learning_object_cuid).get('topic_id')]] = [predicted_learning_object_placements[learning_object_cuid].get('learning_object')]

        new_topic_learning_objects = generate_new_topics(new_topic_learning_objects)

        # Each of these Learning Objects are then passed through
        # a cluster of classification models. Each model will return
        # an array probabilities, indicating a confidence that the
        # speficied Learning Object belongs in a topic.

        return jsonify({'standard_topics': standard_topic_learning_objects, 'new_topics': new_topic_learning_objects }), 200


    # The body for this route should follow the format
    # {
    #   <topic name> : LearningObject[],
    #   <topic name> : LearningObject[],
    #   <topic name> : LearningObject[]
    #   ...
    # }
    @app.route('/topics/assign/update', methods=['POST'])
    def assignNewTopics():

        decoded_token = decode_authorization_jwt(request.headers.get( 'Authorization' ))

        if decoded_token is None:

            return jsonify({ 'message': HTTP_UNAUTHORIZED_MESSAGE }), HTTP_UNAUTHORIZED_CODE

        requester_access_groups = decoded_token.get('accessGroups')

        if requester_access_groups is None or 'admin' not in requester_access_groups and 'editor' not in requester_access_groups:

            return jsonify({ 'message': HTTP_FORBIDDEN_MESSAGE }), HTTP_FORBIDDEN_CODE

        req_data = request.get_json()

        # Get list of topic names 
        new_topic_names = list(req_data.keys())
        topic_names = get_all_topic_names()

        # Compare list of topic names with topic names in given assignment map
        # Upsert topic names into the topic names list
        for new_name in new_topic_names:

            new_name_exists = False

            for existing_name in topic_names:
                if existing_name.lower() == new_name.lower():
                        new_name_exists = True

            if not new_name_exists:
                topic_names.append(new_name)

        # Save new topic names list
        update_topic_name_list(topic_names)

        # Update each Learning Object topic label
        for topic_name in new_topic_names:
            for learning_object in req_data[topic_name]:
                if learning_object.get('id') is not None:
                    id = learning_object.get('id')
                else:
                    id = learning_object.get('_id')
                assign_topic_name(id, topic_name)

        # Invoke Pipeline (CodeBuild)
        invoke_model_training_job()

        return jsonify({'topic_names': topic_names }), 200

