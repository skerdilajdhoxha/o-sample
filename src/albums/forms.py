from django import forms
from django.forms import ClearableFileInput, FileInput, Select, TextInput, models
from django.forms.models import inlineformset_factory

from .models import Album, AlbumCategory, AlbumPhotos


class AlbumCategoryCreateForm(models.ModelForm):
    class Meta:
        model = AlbumCategory
        # fields = '__all__'
        exclude = ("slug", "user", "cat_nr", "parent")


class AlbumCategoryUpdateForm(models.ModelForm):
    class Meta:
        model = AlbumCategory
        # fields = '__all__'
        exclude = ("slug", "user", "cat_nr", "parent")
        widgets = {
            "name": TextInput(attrs={"class": "text-field w-input"}),
            # "parent": Select(attrs={"class": "text-field w-input"}),
            # 'photo': TextInput(attrs={'class': 'blu_invoice_edit_field w-input'}),
            # "photo": ClearableFileInput(attrs={"class": "text-field w-input"}),
        }


class AlbumPhotosForm(forms.ModelForm):
    class Meta:
        model = AlbumPhotos
        exclude = ("created", "updated")


AlbumPhotosFormSet = inlineformset_factory(
    Album, AlbumPhotos, form=AlbumPhotosForm, extra=1
)
