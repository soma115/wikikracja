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

    city = models.CharField(null=True, blank=True, max_length=100)
    hobby = models.CharField(null=True, blank=True, max_length=200)
    to_give_away = models.CharField(null=True, blank=True, max_length=2000)
    to_borrow = models.CharField(null=True, blank=True, max_length=500)
    for_sale = models.CharField(null=True, blank=True, max_length=500)
    i_need = models.CharField(null=True, blank=True, max_length=500)
    skills = models.CharField(null=True, blank=True, max_length=500)
    knowledge = models.CharField(null=True, blank=True, max_length=500)
    want_to_learn = models.CharField(null=True, blank=True, max_length=500)
    business = models.CharField(null=True, blank=True, max_length=200)
    job = models.CharField(null=True, blank=True, max_length=500)

    # fb_profil = models.CharField(null=True, blank=True, max_length=200)
    # foto = models.CharField(null=True, blank=True, max_length=500)
    # i_know_personally_those_important_people = models.CharField(null=True, blank=True, max_length=500)

    # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            # no, there should be no 'self':
            Uzytkownik.objects.create(uid=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.uzytkownik.save()


class Rate(models.Model):
    kandydat = models.ForeignKey(Uzytkownik,
                                 on_delete=models.CASCADE,
                                 related_name='kandydat')
    obywatel = models.ForeignKey(Uzytkownik,
                                 on_delete=models.CASCADE,
                                 related_name='obywatel')
    rate = models.SmallIntegerField(null=True, default=0)

    class Meta:
        unique_together = ('kandydat', 'obywatel')
