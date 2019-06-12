from django.conf.urls import url
from . import views as v

app_name = 'glosowania'

urlpatterns = (
    url(r'^$', v.glosowania, name='index'),
    url(r'^(?P<pk>[0-9]+)/$', v.glosowanie_szczegoly,
        name='glosowanie_szczegoly'),
    url(r'^nowy/$', v.dodaj, name='dodaj_nowy'),
)
