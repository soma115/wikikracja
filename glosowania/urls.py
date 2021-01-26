from django.urls import path
from . import views as v

app_name = 'glosowania'

urlpatterns = (
    path('status/<int:pk>/', v.status, name='status'),
    # http://127.0.0.1:8000/glosowania/details/89/
    path('details/<int:pk>/', v.details, name='details'),
    path('nowy/', v.dodaj, name='dodaj_nowy'),
)
