from django import forms
from obywatele.models import User  # Custom user model
from django.utils.safestring import mark_safe


class ObywatelForm(forms.ModelForm):
    username = forms.CharField(label=mark_safe('<br />Nazwa użytkownika'))
    email = forms.CharField(label=mark_safe('<br />Email'))
    # first_name = forms.CharField(label=mark_safe('<br />imię'))
    # last_name = forms.CharField(label=mark_safe('<br />nazwisko'))

    class Meta:
        model = User
        # fields = ('email', 'first_name', 'last_name')
        fields = ('username', 'email')
