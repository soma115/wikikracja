from django.urls import path
# from django.urls import re_path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat, name='chat'),
    path('add/', views.add, name='add'),
    # path('start', views.chat, name='chat'),
    # path('<str:room_name>/', views.room, name='room_name'),
    # TODO: Link to chat with 1 user (1-to-1 chat)?
]
