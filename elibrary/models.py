from django.db import models
import os
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import FileExtensionValidator
from taggit.managers import TaggableManager
from django.urls import reverse
# base_dir = os.path.abspath('.')


class Book(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200, verbose_name=_('Title'))
    author = models.CharField(null=True, blank=True, max_length=200, verbose_name=_('Author'))
    cover = models.ImageField(null=True, blank=True, upload_to='elibrary',
                              default='elibrary/default.png', verbose_name=_('Cover'),
                              help_text=_('Cover proportions should be 2/3. I.E. width x 1.5 = height')  # doesnt work and I don't know why...
                              )
    file_epub = models.FileField(null=True, blank=True, upload_to='elibrary', verbose_name=_('epub'), validators=[FileExtensionValidator(['epub'])])
    file_mobi = models.FileField(null=True, blank=True, upload_to='elibrary', verbose_name=_('mobi'), validators=[FileExtensionValidator(['mobi'])])
    file_pdf = models.FileField(null=True, blank=True, upload_to='elibrary', verbose_name=_('pdf'), validators=[FileExtensionValidator(['pdf'])])
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    # https://django-taggit.readthedocs.io/en/latest/forms.html
    # tag = TaggableManager(blank=True,
    #                       help_text=_('Groups of characters which appear between double quotes take precedence as multi-word tags (so double quoted tag names may contain commas). An unclosed double quote will be ignored. Otherwise, if there are any unquoted commas in the input, it will be treated as comma-delimited. If not, it will be treated as space-delimited.')
    #                       ) 

    def __str__(self):
        return '%s' % (self.title)

    def get_absolute_url(self):
            # return reverse('elibrary:book-detail', args=[str(self.id)])
            # return reverse('elibrary:book-update', kwargs={'pk': self.pk})
            return reverse('elibrary:book-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = "eBooks"
        ordering = ("id", )

