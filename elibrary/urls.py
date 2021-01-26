from elibrary import views as v
from django.urls import path

app_name = 'elibrary'

urlpatterns = [
    path('', v.IndexView.as_view(), name='elibrary'),
    path('new/', v.add, name='add'),
    path('<pk>/del/', v.BookDelete.as_view(), name='bookdelete'),
]
