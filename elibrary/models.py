from django.db import models
import os
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

base_dir = os.path.abspath('.')


class Ebook(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200, verbose_name=_('Title'))
    cover = models.ImageField(null=True, blank=True, upload_to='.', verbose_name=_('Cover'))
    file1 = models.FileField(null=True, blank=True, upload_to='.', verbose_name=_('File1'))
    file2 = models.FileField(null=True, blank=True, upload_to='.', verbose_name=_('File2'))
    file3 = models.FileField(null=True, blank=True, upload_to='.', verbose_name=_('File3'))
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '%s' % (self.title)

    class Meta:
        verbose_name_plural = "eBooks"
