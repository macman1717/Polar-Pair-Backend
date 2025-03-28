from django.shortcuts import render
from rest_framework.decorators import api_view

import requests
# Create your views here.
from pathlib import Path
import os.path
from datetime import timedelta
from pathlib import Path
from openai import OpenAI
import environ
from rest_framework.response import Response

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


@api_view(["GET"])
def hello_world(request, interest1, interest2):
    token = env("HUGGING_FACE_TOKEN")

    client = OpenAI(
        base_url="https://ijdwa7bxb4pqunwj.us-east4.gcp.endpoints.huggingface.cloud/v1/",
        api_key=token
    )
    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[
            {
                "role": "user",
                "content": f"""
    		"### INSTRUCTION ###
        Generate ONLY the icebreaker question itself with:
        - No 'Person 1/Person 2' labels
        - No introductory phrases
        - No explanations
        - Under 15 words

        ### INTERESTS ###
        - Interest A: [{interest1}]
        - Interest B: [{interest2}]

        ### QUESTION FORMAT ###
        How [related concept] compare [related concept]?

        ### OUTPUT ###
    "
    	Generate exactly one icebreaker question for two people with separate interests:
    - Person A loves [{interest1}]
    - Person B loves [{interest2}]

    Rules:
    1. Output ONLY the question
    2. No introductory phrases
    3. Maximum 12 words
    4. Connect their interests implicitly (no merged activities)

    Bad example (violates rule #2):
    'Here's a question: How would...'

    Good example:
    'How do soccer tactics compare to racing pit-stop strategies?'"
        """
            }
        ],
        top_p=None,
        temperature=None,
        max_tokens=150,
        stream=True,
        seed=None,
        stop=None,
        frequency_penalty=None,
        presence_penalty=None
    )
    prompt_response = ""
    for message in chat_completion:
        prompt_response += message.choices[0].delta.content
    print(prompt_response)


    return Response(prompt_response)



