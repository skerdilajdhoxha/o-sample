from datetime import timedelta

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.forms import DateInput, EmailInput, FileInput, TextInput
from django.utils.datetime_safe import date

from accounts.models import Profile, User


class UserEditForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
        the user, but replaces the password field with admin's
        password hash display field.
        """

    # password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("user_type",)
        # widgets = {
        #     "first_name": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
        #     "last_name": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
        #     "email": EmailInput(attrs={"class": "blu_invoice_edit_field w-input"}),
        # }

    # def clean_password(self):
    #     # Regardless of what the user provides, return the initial value.
    #     # This is done here, rather than on the field, because the
    #     # field does not have access to the initial value
    #     return self.initial["password"]


class UserTypeEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("user_type", "expiration_date")


class ProfileUsernameEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("username", "photo")
        widgets = {
            # "username": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
        }


class ProfilePhotoEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("photo",)
        widgets = {
            # 'photo': FileInput(attrs={'class': 'blu_invoice_edit_field w-input'}),
        }


class ChangePasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
