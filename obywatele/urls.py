from obywatele import views as v
from django.urls import path

app_name = 'obywatele'

urlpatterns = (
    # path('', v.obywatele, name='index'),

    path('', v.obywatele, name='index'),
    path('poczekalnia/', v.poczekalnia, name='poczekalnia'),
    path('poczekalnia/<int:pk>/', v.obywatele_szczegoly, name='obywatele_szczegoly'),
    path('<int:pk>/', v.obywatele_szczegoly, name='obywatele_szczegoly'),
    path('nowy/', v.dodaj, name='zaproponuj_osobe'),
)
