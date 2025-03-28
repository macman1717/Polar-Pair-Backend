from django.contrib.auth.models import User
from django.shortcuts import render
from django_mongodb_backend.dbapi import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tutorial.quickstart.serializers import UserSerializer


# Create your views here.
@api_view(['POST'])
def signup(request):
    data = request.data
    username = data['username']
    password = data['password']
    try:
        user = User.objects.create_user(username=username, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    data = request.data
    username = data['username']
    password = data['password']
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            return Response({"username":user.username}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)