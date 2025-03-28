from django.conf import settings
from django.db import models
from django_mongodb_backend.fields import ArrayField


# Create your models here.
class Room(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.IntegerField()
    name = models.TextField()

class Participant(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.TextField()
    interests = ArrayField(models.TextField())

class Pairing(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    participant1 = models.TextField()
    participant2 = models.TextField()
    icebreaker = models.TextField()