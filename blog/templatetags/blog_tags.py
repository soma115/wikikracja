from django import template

from blog.models import Blog

register = template.Library()


@register.simple_tag
def recent_blogs(limit=10, exclude=None):
    """Returns list of latest blogs"""
    queryset = Blog.objects.filter(published=True).order_by('-modified')
    if exclude:
        if hasattr(exclude, '__iter__'):
            queryset = queryset.exclude(pk__in=exclude)
        else:
            queryset = queryset.exclude(pk=exclude)
    return queryset
