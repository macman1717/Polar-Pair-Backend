from rest_framework import serializers

from main.rooms.models import Room, Pairing


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['code', 'name']

class PairingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pairing
        fields = ['participants1', 'participants2','icebreaker']