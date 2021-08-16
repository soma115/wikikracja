from .views import BlogListView, BlogDetailView
from django.urls import path

app_name = 'blog'

urlpatterns = [
    path('', BlogListView.as_view(), name='blog-list'),
    path('blog/<pk>/', BlogDetailView.as_view(), name='blog-detail'),
]
