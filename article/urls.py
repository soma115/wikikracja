from django.conf.urls import url  #, patterns
from django.urls import include, re_path
from .views import ArticleListView, ArticleView

app_name = 'blog'

urlpatterns = (
    re_path('^$', ArticleListView.as_view(), name='article-list'),
    re_path('^article/(?P<slug>[a-z0-9-]+)/$', ArticleView.as_view(), name='article-detail'),
)
