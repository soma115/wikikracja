from django.contrib import admin
from home import views as hv
from obywatele import views as ov
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from filebrowser.sites import site
from django.views.generic import RedirectView

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/login/'}, name='logout'),
    path('', include('home.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('haslo/', hv.haslo, name='haslo'),
    path('glosowania/', include('glosowania.urls', namespace='glosowania')),
    path('elibrary/', include('elibrary.urls', namespace='elibrary')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('obywatele/', include('obywatele.urls', namespace='obywatele')),
    path('change_email/', ov.change_email, name='change_email'),
    path('accounts/', include('allauth.urls')),
    path('blog/', include('article.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('favicon.ico',RedirectView.as_view(url='/static/home/images/favicon.ico')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''
allauth:
Note that you do not necessarily need the URLs provided by django.contrib.auth.urls.
Instead of the URLs login, logout, and password_change (among others),
you can use the URLs provided by allauth: account_login, account_logout, account_set_password…
'''
