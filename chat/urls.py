from django.conf.urls import url
from . import views

app_name = 'chat'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),

    # url(r'^(?P<ogolny>)/$', views.room, name='ogolny'),
    url(r'^ogolny/$', views.room, name='ogolny'),
    # url(r'^(?P<pk>[0-9]+)/$', v.obywatele_szczegoly,

]
