from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from obywatele.models import Uzytkownik


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Uzytkownik
        fields = ('responsibilities', 'city', 'hobby', 'to_give_away', 'to_borrow', 'for_sale', 'i_need', 'skills', 'knowledge', 'want_to_learn', 'business', 'job', 'fb', 'other')
