from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from obywatele.models import Uzytkownik
from django.utils.translation import ugettext_lazy as _


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class NameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(NameChangeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        self.user.first_name = first_name
        self.user.last_name = last_name
        if commit:
            self.user.save()
        return self.user


class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UsernameChangeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        username = self.cleaned_data["username"]
        self.user.username = username
        if commit:
            self.user.save()
        return self.user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Uzytkownik
        # fields = ('foto', 'phone', 'responsibilities', 'city', 'hobby',
        fields = ('phone', 'responsibilities', 'city', 'hobby',
                  'to_give_away', 'to_borrow', 'for_sale', 'i_need',
                  'skills', 'knowledge', 'want_to_learn', 'business',
                  'job', 'gift', 'other')


class EmailChangeForm(forms.Form):
    """
    A form that lets a user change set their email while checking for a change in the 
    e-mail.
    """
    error_messages = {
        'email_mismatch': _("The two email addresses fields didn't match."),
        'not_changed': _("The email address is the same as the one already defined."),
    }

    new_email1 = forms.EmailField(
        label=_("New email address"),
        widget=forms.EmailInput,
    )

    new_email2 = forms.EmailField(
        label=_("New email address confirmation"),
        widget=forms.EmailInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self):
        old_email = self.user.email
        new_email1 = self.cleaned_data.get('new_email1')
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages['not_changed'],
                    code='not_changed',
                )
        return new_email1

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_email2

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user