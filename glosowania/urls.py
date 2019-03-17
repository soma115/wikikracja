from django.conf.urls import url
from glosowania import views as vviews

urlpatterns = (
    url(r'^$', vviews.glosowania, name='glosowania'),
    url(r'^(?P<pk>[0-9]+)/$', vviews.glosowanie_szczegoly, name='glosowanie_szczegoly'),
    url(r'^nowy/$', vviews.dodaj, name='dodaj_nowy'),
)
