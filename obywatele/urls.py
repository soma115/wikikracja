from obywatele import views as v
from django.urls import path
from obywatele.models import Uzytkownik
from django.contrib.auth.decorators import login_required

app_name = 'obywatele'

urlpatterns = (
    path('', v.obywatele, name='obywatele'),
    path('poczekalnia/', v.poczekalnia, name='poczekalnia'),
    path('poczekalnia/<int:pk>/', v.obywatele_szczegoly, name='poczekalnia_szczegoly'),
    path('<int:pk>/', v.obywatele_szczegoly, name='obywatele_szczegoly'),
    path('my_profile/', v.my_profile, name='my_profile'),
    path('my_assets/', v.my_assets, name='my_assets'),
    path('nowy/', v.dodaj, name='zaproponuj_osobe'),
    path('change_name/', v.change_name, name='change_name'),
    path('change_username/', v.change_username, name='change_username'),
    path("assets/", login_required(v.AssetListView.as_view()), name='assets')
)
