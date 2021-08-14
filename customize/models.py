from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField


class Customize(models.Model):
    title = models.CharField(max_length=200)
    # content = models.TextField()
    content = HTMLField()
    mod_date = models.DateField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
