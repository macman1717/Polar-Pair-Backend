from django.shortcuts import render
from rest_framework.decorators import api_view

import requests
# Create your views here.
from pathlib import Path
import os.path
from datetime import timedelta
from pathlib import Path
import environ
from rest_framework.response import Response

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


@api_view("GET")
def hello_world(request, interest1, interest2):
    token = env("HUGGING_FACE_TOKEN")
    ENDPOINT_URL = "https://ub7033fgvvexdwvr.us-east-1.aws.endpoints.huggingface.cloud"
    headers = {"Authorization": token}
    prompt = f"""
    Generate a fun, open-ended icebreaker question for:
    - Person 1 who loves {interest1}
    - Person 2 who loves {interest2}
    Make it creative and specific!
    """
    payload = {"inputs": prompt}
    response = requests.post(ENDPOINT_URL, headers=headers, json=payload)
    return Response(response.json()[0]['generated_text'])



