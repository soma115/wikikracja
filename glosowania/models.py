import os
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list
import re

base_dir = os.path.abspath('.')

def does_it_exist(value):
    x = re.split('\W+', value.strip(' ').strip(',').strip(' ').strip(',').strip(' ').strip(',').strip(' ').strip(','))
    for i in x:
        try:
            existing = Decyzja.objects.get(pk=int(i))  # all existing for now
        except Exception as e:
            raise ValidationError(_("Enter only existing bill numbers here"))
    return True

class Decyzja(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.TextField(
    max_length=200,
    null=True,
    verbose_name=_('Title'),
    help_text=_('Enter short title describing new law.')
    )
    tresc = models.TextField(
        max_length=500,
        null=True,
        verbose_name=_('Law text'),
        help_text=_('Enter the exact wording of the law as it is to be applied.')
        )
    kara = models.TextField(
        max_length=500,
        null=True,
        verbose_name=_('Penalty'),
        help_text=_('What is the penalty for non-compliance with this rule. This can be, for example: "Banishment for 3 months", "Banishment forever", etc.')
        )
    uzasadnienie = models.TextField(
        max_length=1500,
        null=True,
        verbose_name=_('Reasoning'),
        help_text=_('What events inspired this bill? What are we going to achieve with it?')
        )
    args_for = models.TextField(
        max_length=1500,
        null=True,
        verbose_name=_('Positive Aspects of the Idea'),
        help_text=_('Enter the benefits for the group, environment, economy, etc. resulting from the introduction of the idea.')
        )
    # TODO: This field should be filled out by anyone:
    args_against = models.TextField(
        max_length=1500,
        null=True,
        verbose_name=_('Negative Aspects of the Idea'),
        help_text=_('Enter the potential threat associated with the proposal.')
        )
    
    znosi = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_('Abolishes the rules'),
        help_text=_('If the proposed law supersedes other bills, enter their numbers here.'),
        validators=[validate_comma_separated_integer_list, does_it_exist],
        )

    ile_osob_podpisalo = models.SmallIntegerField(editable=False, default=0)
    data_powstania = models.DateField(auto_now_add=True,
                                      editable=False,
                                      null=True)
    data_zebrania_podpisow = models.DateField(editable=False, null=True)
    data_referendum_start = models.DateField(editable=False, null=True)
    data_referendum_stop = models.DateField(editable=False, null=True)
    data_zatwierdzenia = models.DateField(editable=False, null=True)
    data_obowiazuje_od = models.DateField(editable=False, null=True)
    za = models.SmallIntegerField(default=0, editable=False)
    przeciw = models.SmallIntegerField(default=0, editable=False)
    status = models.SmallIntegerField(default=1, editable=False)

    # 1.Propozycja, 2.Brak poparcia, 3.W kolejce, 4.Referendum, 5.Odrzucone,
    # 6.Zatwierdzone/Vacatio Legis, 7.Obowiązuje

    def __str__(self):
        return '%s: %s on %s' % (self.pk, self.tresc, self.status)

    objects = models.Manager()


class ZebranePodpisy(models.Model):
    '''Lista podpisów pod wnioskiem o referendum'''
    projekt = models.ForeignKey(Decyzja, on_delete=models.CASCADE)

    # Lets note who signed proposal:
    podpis_uzytkownika = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('projekt', 'podpis_uzytkownika')


class KtoJuzGlosowal(models.Model):
    projekt = models.ForeignKey(Decyzja, on_delete=models.CASCADE)
    ktory_uzytkownik_juz_zaglosowal = models.ForeignKey(User, on_delete=models.CASCADE)

    # odnotowujemy tylko fakt głosowania

    class Meta:
        unique_together = ('projekt', 'ktory_uzytkownik_juz_zaglosowal')


class VoteCode(models.Model):
    '''
    - Jednorazowy kod
    - Tak/Nie
    '''
    project = models.ForeignKey(Decyzja, on_delete=models.CASCADE)
    code = models.CharField(editable=False, null=True, max_length=20)
    vote = models.BooleanField(editable=False, null=True)
    