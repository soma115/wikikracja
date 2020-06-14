from django.db import models
from django.utils import timezone


# Create your models here.
class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)

    def __unicode__(self):
        return self.label
