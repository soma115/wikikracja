from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    # users = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return '%s' % (self.label)

    def addUser():
        pass


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField(auto_now=True)
    text = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    # TODO: revisions (editMessage(), deleteMessage())
