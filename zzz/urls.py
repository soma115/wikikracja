from django.contrib import admin
from home import views as hv
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
  path('', include('home.urls')),
  path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
  path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/login/'}, name='logout'),
  path('haslo/', hv.haslo, name='haslo'),
  path('admin/', admin.site.urls),
  path('glosowania/', include('glosowania.urls', namespace='glosowania')),
  path('obywatele/', include('obywatele.urls', namespace='obywatele')),
  path('elibrary/', include('elibrary.urls', namespace='elibrary')),
  path('chat/', include('chat.urls', namespace='chat')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
