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
    foto = models.ImageField(upload_to='obywatele', default='obywatele/anonymous.png', null=True, blank=True, verbose_name=_('Foto'))
    phone = models.CharField(null=True, blank=True, max_length=20, help_text=_('Phone number i.e. +48 123 456 789'), verbose_name=_('Phone number'))
    responsibilities = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Tasks performed in our group'), verbose_name=_('Responsibilities'))
    city = models.CharField(null=True, blank=True, max_length=100, help_text=_('Where one spend most of their time'), verbose_name=_('City'))
    hobby = models.CharField(null=True, blank=True, max_length=2000, help_text=_('Hobbies one have'), verbose_name=_('Hobby'))
    to_give_away = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Things you are willing to give away for free'), verbose_name=_('To give away'))
    to_borrow = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Stuff you can borrow to others'), verbose_name=_('To borrow'))
    for_sale = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Stuff you have for sale'), verbose_name=_('For sale'))
    i_need = models.TextField(null=True, blank=True, max_length=2000, help_text=_('What do you need'), verbose_name=_('I need'))
    skills = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Practical skills one have'), verbose_name=_('Skills'))
    knowledge = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Knowledge one have'), verbose_name=_('Knowledge'))
    want_to_learn = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Things one would like to learn'), verbose_name=_('I want to learn'))
    business = models.TextField(null=True, blank=True, max_length=2000, help_text=_('If running a business'), verbose_name=_('Business'))
    job = models.CharField(null=True, blank=True, max_length=2000, help_text=_('Profession'), verbose_name=_('Job'))
    fb = models.CharField(null=True, blank=True, max_length=500, help_text=_('Link to Facebook profile'), verbose_name=_('Facebook'))
    gift = models.CharField(null=True, blank=True, max_length=500, help_text=_('What gift would you like to receive'), verbose_name=_('Gift'))
    other = models.TextField(null=True, blank=True, max_length=2000, help_text=_('Other things worth mentioning'), verbose_name=_('Other'))
    # i_know_personally_those_important_people = models.CharField(null=True, blank=True, max_length=500)
    class Meta:
        verbose_name = _("Citizen")
        verbose_name_plural = _("Citizens")

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
