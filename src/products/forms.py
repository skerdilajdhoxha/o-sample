from django import forms
from django.forms import FileInput, Select, TextInput, models
from django.forms.models import inlineformset_factory

from .models import Product, ProductCategory, ProductPhotos


class ProductCategoryCreateForm(models.ModelForm):
    class Meta:
        model = ProductCategory
        exclude = ("slug", "user", "cat_nr", "parent")


class ProductCategoryUpdateForm(models.ModelForm):
    class Meta:
        model = ProductCategory
        exclude = ("slug", "user", "cat_nr", "parent")
        widgets = {
            # "name": TextInput(attrs={"class": "text-field w-input"}),
            # "parent": Select(attrs={"class": "text-field w-input"}),
            # 'photo': TextInput(attrs={'class': 'blu_invoice_edit_field w-input'}),
            # "photo": FileInput(attrs={"class": "blu_invoice_edit_field w-input"}),
        }


class ProductEditForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ("created", "updated", "categories", "slug", "user")


class ProductPhotosForm(forms.ModelForm):
    class Meta:
        model = ProductPhotos
        exclude = ("created", "updated")


ProductPhotosFormSet = inlineformset_factory(
    Product, ProductPhotos, form=ProductPhotosForm, extra=1
)
