from django.views.generic import DetailView, ListView
from django.conf import settings

from .models import Blog


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/detail.html'


class BlogListView(ListView):
    model = Blog
    template_name = 'blog/list.html'
    paginate_by = getattr(settings, 'ARTICLE_PAGINATE_BY', None)

    def get_queryset(self):
        queryset = super(BlogListView, self).get_queryset()
        # return queryset.filter(published=True)
        return queryset
