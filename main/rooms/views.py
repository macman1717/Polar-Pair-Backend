import os
import random
from random import randint

import environ
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from google.cloud import storage
from google.oauth2 import service_account
from openai import OpenAI
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Participant, Room, Pairing
from .serializers import PairingSerializer

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

creds = {
    "type": env("TYPE"),
    "project_id": env("PROJECT_ID"),
    "private_key_id": env("PRIVATE_KEY_ID"),
    "private_key": env('PRIVATE_KEY').replace('\\n', '\n').replace('"',''),
    "client_email": env("CLIENT_EMAIL"),
    "client_id": env("CLIENT_ID"),
    "auth_uri": env("AUTH_URI"),
    "token_uri": env("TOKEN_URI"),
    "auth_provider_x509_cert_url": env("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": env("CLIENT_X509_CERT_URL"),
    "universe_domain": env("UNIVERSE_DOMAIN"),
}

base_url = "https://storage.googleapis.com/images21307/"


# Create your views here.
@api_view(['POST'])
def create_room(request, username, room_name):
    try:
        user = User.objects.get(username=username)
        room_code = randint(10000, 99999)
        user.room_set.create(name=room_name, code=room_code)
        return Response({'code': room_code, 'room_name': room_name})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status= status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_room(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
        room.delete()

        credentials = service_account.Credentials.from_service_account_info(creds)
        client = storage.Client(credentials=credentials, project=creds["project_id"])

        bucket = client.get_bucket('images21307')
        blobs_to_delete = []
        for blob in bucket.list_blobs():
            if blob.name.startswith(f"{room_code}&"):
                blobs_to_delete.append(blob)

        if blobs_to_delete:
            bucket.delete_blobs(blobs_to_delete)
        return Response({'code': 200})
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_room(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
        return Response({'code': 200, 'room_name': room.name})
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_participant(request, room_code):
    participant_name = request.data.get('name')
    interests = request.data.get('interests')
    participant_interests = interests.split(',')
    image_file = request.data.get('image')


    try:
        credentials = service_account.Credentials.from_service_account_info(creds)
        client = storage.Client(credentials=credentials, project=creds["project_id"])

        bucket = client.get_bucket('images21307')
        filename = room_code + "&" + participant_name
        blob = bucket.blob(filename)

        room = Room.objects.get(code=room_code)
        room.participant_set.create(name=participant_name, interests=participant_interests)

        blob.upload_from_file(file_obj=image_file, content_type='image/png')

        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(repr(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_participant(request, room_code, name):
    try:
        room = Room.objects.get(code=room_code)
        participant = room.participant_set.get(name=name)

        filename = room_code + "&" + name
        credentials = service_account.Credentials.from_service_account_info(creds)
        client = storage.Client(credentials=credentials, project=creds["project_id"])
        bucket = client.get_bucket('images21307')
        blob = bucket.blob(filename)
        blob.delete()
        participant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_pairings(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
        Pairing.objects.filter(room=room).delete()
        participants = list(Participant.objects.filter(room=room))
        random.shuffle(participants)
        index = 0
        while index < len(participants):
            participant1 = participants[index]
            index += 1
            participant2 = participants[index]
            index += 1

            interests = participant1.interests
            random.shuffle(interests)
            interest1 = interests[0]
            interests = participant2.interests
            random.shuffle(interests)
            interest2 = interests[0]
            if interest1 == interest2:
                interest2 = interests[1]
            icebreaker = prompt(interest1, interest2)
            room.pairing_set.create(participant1=participant1.name, participant2=participant2.name, icebreaker=icebreaker)

        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_pairings(request, room_code, name):
    try:
        room = Room.objects.get(code=room_code)
        pairing = room.pairing_set.filter(Q(participant1=name) | Q(participant2 = name))[0]
        if pairing.participant1 == name:
            return Response({"partner":pairing.participant2, "picture":base_url+room_code+"&"+pairing.participant2, "icebreaker":pairing.icebreaker}, status=status.HTTP_200_OK)
        else:
            return Response({"partner":pairing.participant1, "picture":base_url+room_code+"&"+pairing.participant2, "icebreaker":pairing.icebreaker}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_pairings(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
        pairings = room.pairing_set.all()
        pairings_list = []
        for pairing in pairings:
            pairings_list.append({
                "Person A": pairing.participant1,
                "Person B": pairing.participant2,
                "icebreaker": pairing.icebreaker
            })
        return Response({"pairings":pairings_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_participants(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
        participants = room.participant_set.all()
        participant_list = []
        for participant in participants:
            participant_list.append({
                "name":participant.name,
                "interests":participant.interests
            })
        return Response({"participants":participant_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_rooms(request, username):
    try:
        user = User.objects.get(username=username)
        rooms = user.room_set.all()
        room_list = []
        for room in rooms:
            room_list.append({"room_name":room.name,
                              "code": room.code})
        return Response({"rooms":room_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

def prompt(interest1, interest2):
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

    return prompt_response