## Topic Service

### Available Routes

#### GET /topics/assign

Authentication - expected bearer token
Authorization - must be admin or editor

Returns a map containing predicted topics for all unassigned Learning Objects

### POST /topics/assign/update

Authentication - expected bearer token
Authorization - must be admin or editor

Body |
    {
    topic_name : LearningObject[],
    topic_name : LearningObject[],
    topic_name : LearningObject[]
    ...
    }

Updates topic information with the given map

#### GET /learning-objects/unassigned

Authentication - expected bearer token
Authorization - must be admin or editor

Returns a list of unassigned Learning Objects

#### GET /topics

Returns a list of all available topic names
