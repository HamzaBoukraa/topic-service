from flask import jsonify, request
from services.elasticsearch_driver import get_learning_objects_without_topic
from services.mongodb_driver import get_all_topic_names, update_topic_name_list
from controllers.auth import decode_authorization_jwt
from controllers.constants import HTTP_OK_CODE, HTTP_FORBIDDEN_CODE, HTTP_UNAUTHORIZED_CODE, HTTP_UNAUTHORIZED_MESSAGE, HTTP_FORBIDDEN_MESSAGE

def TopicBrowseController(app):

    @app.route('/learning-objects/unassigned', methods=[ 'GET' ])
    def get_unassigned_learning_objects():

        decoded_token = decode_authorization_jwt(request.headers.get( 'Authorization' ))

        if decoded_token is None:

            return jsonify({ 'message': HTTP_UNAUTHORIZED_MESSAGE }), HTTP_UNAUTHORIZED_CODE

        requester_access_groups = decoded_token.get('accessGroups')

        if requester_access_groups is None or 'admin' not in requester_access_groups or 'editor' not in requester_access_groups:

            return jsonify({ 'message': HTTP_FORBIDDEN_MESSAGE }), HTTP_FORBIDDEN_CODE
    
        learning_objects_without_topic = get_learning_objects_without_topic()

        return jsonify({ 'unassigned_learning_objects': learning_objects_without_topic }), HTTP_OK_CODE


    @app.route('/topics', methods=[ 'GET' ])
    def get_topic_names():
        
        topic_names = get_all_topic_names()

        return jsonify({ 'topics': topic_names }), HTTP_OK_CODE



