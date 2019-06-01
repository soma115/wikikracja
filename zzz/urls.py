from django.contrib import admin
from django.conf import settings
from home import views as hv
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
  url(r'^', include('home.urls')),
  url(r'^login/$',
      auth_views.LoginView.as_view(template_name='home/login.html'),
      name='login'),
  url(r'^logout/$',
      auth_views.LogoutView.as_view(), {'next_page': '/login/'},
      name='logout'),
  url(r'^haslo/', hv.haslo, name='haslo'),
  url(r'^admin/', admin.site.urls),
  url(r'^glosowania/', include('glosowania.urls'), name='glosowania'),
  url(r'^obywatele/', include('obywatele.urls'), name='obywatele'),
  url(r'^elibrary/', include('elibrary.urls', namespace='elibrary')),
  # reset password
  # https://simpleisbetterthancomplex.com/tutorial/2016/09/19/how-to-create-password-reset-view.html
  url(r'^password_reset/$',
      auth_views.PasswordResetView.as_view(
          template_name='home/password_reset_form.html'),
      name='password_reset'),
  url(r'^password_reset/done/$',
      auth_views.PasswordResetDoneView.as_view(
          template_name='home/password_reset_done.html'),
      name='password_reset_done'),
  url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
      auth_views.PasswordResetConfirmView.as_view(
          template_name='home/password_reset_confirm.html'),
      name='password_reset_confirm'),
  url(r'^reset/done/$',
      auth_views.PasswordResetCompleteView.as_view(
          template_name='home/password_reset_complete.html'),
      name='password_reset_complete'),


  # url(r'^offer/new/$', onv.offer_new, name='offer_new'),
  # url(r'^offer/(?P<pk>[0-9]+)/$', onv.offer_detail, name='offer_detail'),
  # url(r'^offer/(?P<pk>[0-9]+)/edit/$', onv.offer_edit, name='offer_edit'),
  # url(r'^need/new/$', onv.need_new, name='need_new'),
  # url(r'^need/(?P<pk>[0-9]+)/$', onv.need_detail, name='need_detail'),
  # url(r'^need/(?P<pk>[0-9]+)/edit/$', onv.need_edit, name='need_edit'),
  # url(r'^category/new/$', onv.category_new, name='category_new'),
  # url(r'^category/(?P<pk>[0-9]+)/$', onv.category_detail,
  #     name='category_detail'),
  # url(r'^category/(?P<pk>[0-9]+)/edit/$', onv.category_edit,
  #     name='category_edit'),
  # url(r'^uzytkownik/(?P<pk>[0-9]+)/$', vviews.obywatele_szczegoly,
  #     name='obywatele_szczegoly1'),
  # url(r'^__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
