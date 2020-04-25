import boto3
import os
 
codebuild = boto3.client('codebuild', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

def invoke_model_training_job():
    codebuild.start_build(projectName='Topic-Model-Builder')
