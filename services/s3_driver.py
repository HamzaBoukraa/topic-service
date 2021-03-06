import boto3
import os
 
s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

def download_models():
    s3.download_file(Key='codebuild/cnn_classifier.sav', Filename='cnn_classifier.sav', Bucket='topic-classification-models')
    s3.download_file(Key='codebuild/rnn_classifier.sav', Filename='rnn_classifier.sav', Bucket='topic-classification-models')
    s3.download_file(Key='codebuild/bidirectional_rnn_classifier.sav', Filename='bidirectional_rnn_classifier.sav', Bucket='topic-classification-models')