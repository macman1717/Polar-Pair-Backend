from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
@api_view(['POST'])
def create_room(request, username, room_name):
    try:
        user = User.objects.get(username=username)
        room_code = 2
        user.room_set.create(name=room_name)
        return Response({'code': room_code, 'room_name': room_name})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status= status.HTTP_404_NOT_FOUND)
