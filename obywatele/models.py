from __future__ import unicode_literals

from django.db import models
# from django.utils.timezone import now as dzis
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):  # Overrid standard User model
    # TODO: date_joined powinno być wraz z przyjęciem do obywateli
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    username = models.CharField(_('username'), max_length=30, blank=False,
                                unique=True)
    email = models.EmailField(_('email address'), unique=True)
    # TODO: Przyda się przy przenoszeniu zliczania na koniec dnia. A tymczasem 
    # muszę aktywować superusera ręcznie przy stawianiu instancji.
    is_active = models.BooleanField(_('is_active'), default=False)
    is_staff = models.BooleanField(_('is_staff'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:	
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Uzytkownik(models.Model):
    uid = models.OneToOneField(User, on_delete=models.CASCADE, editable=False, null=True)

    reputacja = models.SmallIntegerField(null=True, default=0)
    polecajacy = models.CharField(editable=False, null=True, max_length=64)
    data_przyjecia = models.DateField(null=True, editable=False)

    # TODO: zrobić rangi: sędzia, senator, administrator
    # ranga =

    # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            # no, there should be no 'self':
            Uzytkownik.objects.create(uid=instance)  

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.uzytkownik.save()


class AkceptacjaOsoby(models.Model):
    kandydat = models.ForeignKey(Uzytkownik,
                                 on_delete=models.CASCADE,
                                 related_name='kandydat')
    obywatel = models.ForeignKey(Uzytkownik,
                                 on_delete=models.CASCADE,
                                 related_name='obywatel')

    class Meta:
        unique_together = ('kandydat', 'obywatel')
