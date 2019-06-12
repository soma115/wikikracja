from django.conf.urls import url
from obywatele import views as v
from django.urls import path

app_name = 'obywatele'

urlpatterns = (
    path('', v.obywatele, name='index'),

    # url(r'^$', v.obywatele, name='index'),
    url(r'^poczekalnia/$', v.poczekalnia, name='poczekalnia'),
    url(r'^poczekalnia/(?P<pk>[0-9]+)/$', v.obywatele_szczegoly,
        name='obywatele_szczegoly'),
    url(r'^(?P<pk>[0-9]+)/$', v.obywatele_szczegoly,
        name='obywatele_szczegoly'),
    url(r'^nowy/$', v.dodaj, name='zaproponuj_osobe'),
)
