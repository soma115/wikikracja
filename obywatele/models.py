from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Uzytkownik(models.Model):
    uid = models.OneToOneField(User,
                               on_delete=models.CASCADE,
                               editable=False,
                               null=True)

    reputation = models.SmallIntegerField(null=True, default=0)
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
    rate = models.SmallIntegerField(null=True, default=0)

    class Meta:
        unique_together = ('kandydat', 'obywatel')
