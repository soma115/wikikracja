from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Uzytkownik(models.Model):
    uid = models.OneToOneField(User,
                               on_delete=models.CASCADE,
                               editable=False,
                               null=True)

    reputation = models.SmallIntegerField(null=True, default=0)
    polecajacy = models.CharField(editable=False, null=True, max_length=64)
    data_przyjecia = models.DateField(null=True, editable=False)

    responsibilities = models.CharField(null=True, blank=True, max_length=2000, help_text=_('Tasks performed in our group'))
    city = models.CharField(null=True, blank=True, max_length=100, help_text=_('Where you are spending most of your time'))
    hobby = models.CharField(null=True, blank=True, max_length=200, help_text=_('Hobbies you have'))
    to_give_away = models.CharField(null=True, blank=True, max_length=2000, help_text=_('Things you are willing to give away for free'))
    to_borrow = models.CharField(null=True, blank=True, max_length=500, help_text=_('Stuff you can borrow to others'))
    for_sale = models.CharField(null=True, blank=True, max_length=500, help_text=_('Stuff you have for sale'))
    i_need = models.CharField(null=True, blank=True, max_length=500, help_text=_('What do you need'))
    skills = models.CharField(null=True, blank=True, max_length=500, help_text=_('What practical skills do you have'))
    knowledge = models.CharField(null=True, blank=True, max_length=500, help_text=_('Knowledge you have'))
    want_to_learn = models.CharField(null=True, blank=True, max_length=500, help_text=_('Things you would like to learn'))
    business = models.CharField(null=True, blank=True, max_length=200, help_text=_('If you are running a business'))
    job = models.CharField(null=True, blank=True, max_length=500, help_text=_('Your profession'))
    fb = models.CharField(null=True, blank=True, max_length=500, help_text=_('Link to Facebook profile'))
    other = models.CharField(null=True, blank=True, max_length=500, help_text=_('Other things about worth mentioning'))

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
