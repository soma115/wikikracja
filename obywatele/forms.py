from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from obywatele.models import Uzytkownik


class ObywatelForm(forms.ModelForm):
    # username = forms.CharField(label=mark_safe('<br />Nazwa użytkownika'))
    # email = forms.CharField(label=mark_safe('<br />Email'))
    # first_name = forms.CharField(label=mark_safe('<br />imię'))
    # last_name = forms.CharField(label=mark_safe('<br />nazwisko'))

    class Meta:
        model = User
        # fields = ('email', 'first_name', 'last_name')
        fields = ('username', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Uzytkownik
        # fields = ('city', 'hobby', 'business_job', 'fb_profil', 'to_give_away', 'to_borrow', 'for_sale', 'i_need', 'i_want_to_learn', 'foto', 'i_know_personally_those_important_people', 'skills', 'knowledge')
        fields = ('city', 'hobby', 'to_give_away', 'to_borrow', 'for_sale', 'i_need', 'skills', 'knowledge', 'want_to_learn', 'business', 'job')
