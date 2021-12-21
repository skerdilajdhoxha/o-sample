from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.forms import DateInput, EmailInput, FileInput, TextInput

from .models import Profile, User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    # groups = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None)

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "user_type")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("email", "password", "is_active", "is_staff")

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {
            "first_name": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            "last_name": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            "email": EmailInput(attrs={"class": "blu_invoice_edit_field w-input"}),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"
        widgets = {
            "username": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            "date_of_birth": DateInput(
                attrs={"class": "blu_invoice_edit_field w-input"}
            ),
            # 'photo': FileInput(attrs={'class': 'blu_invoice_edit_field w-input'}),
        }
