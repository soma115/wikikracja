from django.conf.urls import url
from django.views.generic import TemplateView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^contact/$', TemplateView.as_view(template_name="home/contact.html"),
        name='contact'),

    # reset password
    # https://simpleisbetterthancomplex.com/tutorial/2016/09/19/how-to-create-password-reset-view.html
    url(r'^password_reset/$',
        auth_views.PasswordResetView.as_view(template_name='home/password_reset_form.html'), name='password_reset'),
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
]
