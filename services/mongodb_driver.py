from pymongo import MongoClient
import ssl
import os

client = MongoClient(os.environ.get('MONGODB_CONNECTION'), ssl_cert_reqs=ssl.CERT_NONE)
topics_collection = client.onion.topics
pipeline_status_collection = client.onion.pipelinestatus

def get_all_topic_names():
    # The Topics collection should only ever have one document
    document = list(topics_collection.find())[0]

    return document.get('topics')

def update_topic_name_list(topic_name_list):
    topics_collection.update_one({}, { '$set': { 'topics':  topic_name_list } })

def getPipelineStatus():
    doc = pipeline_status_collection.find();
    return doc