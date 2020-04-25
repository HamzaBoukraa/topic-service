import requests
import json
import os

def get_learning_objects_without_topic():
    body = json.dumps({
        "size": 1000, 
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                { 
                                    "term": { 
                                        "status": "released" 
                                    } 
                                },
                            ],
                            "must_not": [
                                {
                                    "exists": {
                                        "field": "topic"
                                    }
                                }
                            ]
                        },
                    },
                ],
            },
        },
    })

    es_response = requests.post(os.environ.get('ELASTICSEARCH_SEARCH_ROUTE'), data=body, headers={'Content-Type': 'application/json'})

    learning_object_es_documents = json.loads(es_response.text)['hits']['hits']

    learning_objects = []

    for learning_object_es_document in learning_object_es_documents:
        
        learning_object = learning_object_es_document['_source']
        learning_objects.append(learning_object)

    return learning_objects

def assign_topic_name():
    for learning_object in learning_objects:
        learning_object_name = learning_object.get('name')

        query_body = {
            "query": {
                "match": {
                    "id": learning_object.get("_id")
                }
            }
        }
        doc = es.search(index="learning-objects", body=query_body)
        res = es.update(index="learning-objects", doc_type="_doc", id=doc['hits']['hits'][0]['_id'], body={'doc': {'topic': sorted_topics[i].lower()}})


