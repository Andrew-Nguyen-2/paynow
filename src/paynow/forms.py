from django import forms
from accounts.models import OrgUser
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


class ContactForm(forms.Form):
    first = forms.CharField(max_length=50)
    last = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=150)
    message = forms.CharField(widget=forms.Textarea, max_length=2000)


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150)
    password = forms.PasswordInput()


class NewUserForm(UserCreationForm):
    email = forms.EmailField(label=_('Email Address'), required=True, help_text="Required.")

    class Meta:
        model = OrgUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

