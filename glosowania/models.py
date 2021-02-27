import os
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

base_dir = os.path.abspath('.')


class Decyzja(models.Model):
    autor = models.CharField(max_length=200)
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
        help_text=_('What is the purpose of this law? Why was it created? What are we going to achieve with it? What event caused it to arise?')
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
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Abolishes the rules'),
        help_text=_('If the proposed law supersedes other recipes, enter their numbers here.')
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

    # 0.Propozycja, 1.Brak poparcia, 2.W kolejce, 3.Referendum, 4.Odrzucone,
    # 5.Zatwierdzone/Vacatio Legis, 6.Obowiązuje

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
