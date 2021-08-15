from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField


class Customize(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200)
    # content = models.TextField()
    content = HTMLField(null=True, blank=True)
    mod_date = models.DateField(null=True, blank=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
