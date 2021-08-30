from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from taggit.managers import TaggableManager


class Article(models.Model):
    """Simple article model with basic fields"""
    title = models.CharField(_('Title'), max_length=255)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Author"))
    slug = models.SlugField(_('Slug'), max_length=255, unique=True, blank=True)
    summary = HTMLField(_('Summary'), null=True)
    modified = models.DateTimeField(_('Modified'), default=datetime.now)
    published = models.BooleanField(default=True, verbose_name=_("Published"))
    public = models.BooleanField(default=False, verbose_name=_("Public"))
    body = HTMLField(_('Body'), null=True)
    # tags = TaggableManager()  # not clickable and lacking treanslation

    class Meta:
        ordering = ['-modified']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    def __str__(self):
        return f"{self.title} {self.author}"

    def get_absolute_url(self):
        return reverse('blog:article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slug = slugify(self.title)
            counter = 1
            while self.__class__.objects.filter(slug=self.slug).exists():
                self.slug = '{0}-{1}'.format(slug, counter)
            counter += 1
        return super(Article, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)