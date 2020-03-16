import requests
import json

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

    es_response = requests.post('http://elasticsearch:9200/learning-objects/_search', data=body, headers={'Content-Type': 'application/json'})

    learning_object_es_documents = json.loads(es_response.text)['hits']['hits']

    learning_objects = []

    for learning_object_es_document in learning_object_es_documents:
        
        learning_object = learning_object_es_document['_source']
        learning_objects.append(learning_object)

    return learning_objects


