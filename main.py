from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

from controllers.topic_browse_controller import TopicBrowseController
from controllers.topic_prediction_controller import TopicPredictionController

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r'/*': { 'origins': os.environ.get('CLIENT_DOMAIN') }}, supports_credentials=True)

topic_browse_controller = TopicBrowseController(app)
topic_prediction_controller = TopicPredictionController(app)    

@app.route('/')
def index():
    return jsonify({ 'message': 'Welcome to the Clark Topic Service' }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)


