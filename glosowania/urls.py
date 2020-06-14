from django.urls import path
from . import views as v

app_name = 'glosowania'

urlpatterns = (
    path('', v.glosowania, name='index'),
    path('<int:pk>/', v.glosowanie_szczegoly, name='glosowanie_szczegoly'),
    path('nowy/', v.dodaj, name='dodaj_nowy'),
)
