from django.urls import path
# from django.urls import re_path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat, name='chat'),
    path('add_room/', views.add_room, name='add_room'),
    # path('start', views.chat, name='chat'),
    # path('<str:room_name>/', views.room, name='room_name'),
]
