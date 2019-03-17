from django.db import models
import os
from django.db import models
import datetime
from django.contrib.auth.models import User

base_dir = os.path.abspath('.')


class Ebook(models.Model):
	title = models.CharField(max_length=200, verbose_name='Tytuł')
	file = models.FileField(upload_to='.', verbose_name='Plik')
	uploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return '%s' % (self.title)

	class Meta:
		verbose_name_plural = "eBooks"
