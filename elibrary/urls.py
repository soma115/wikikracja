from django.conf.urls import url
from elibrary import views as v

app_name = 'elibrary'

urlpatterns = [
    # /elibrary/
    url(r'^$', v.IndexView.as_view(), name='index'),
    # /elibrary/add/
    url(r'^new/$', v.add, name='add'),
    # /elibrary/2/delete
    url(r'^(?P<pk>[0-9]+)/del/$', v.BookDelete.as_view(), name='bookdelete'),
]
