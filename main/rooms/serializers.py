from rest_framework import serializers

from .models import Room, Pairing


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['code', 'name']

class PairingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pairing
        fields = ['participant1', 'participant2','icebreaker']