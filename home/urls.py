from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^contact/$', TemplateView.as_view(template_name="home/contact.html"), name='contact'),
]
