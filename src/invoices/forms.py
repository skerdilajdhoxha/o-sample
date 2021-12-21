from django import forms
from django.forms import EmailInput, NumberInput, Textarea, TextInput, models

from .models import Invoice


class InvoiceCreateForm(models.ModelForm):
    class Meta:
        model = Invoice
        exclude = (
            "user",
            "slug",
            "pdf",
            "image",
            "invoice_nr",
            "invoice_number",
        )
        widgets = {
            "visible_notes": Textarea(attrs={"rows": 4, "cols": 15}),
            "private_notes": Textarea(attrs={"rows": 4, "cols": 15}),
        }


class InvoiceUpdateForm(models.ModelForm):
    class Meta:
        model = Invoice
        exclude = (
            "user",
            "slug",
            "pdf",
            "image",
            "invoice_nr",
            "invoice_number",
        )
        labels = {"invoice_title": "", "content": ""}
        widgets = {
            # "invoice_title": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "invoice_nr": NumberInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "customer_company_name": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "customer_name": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "customer_email": EmailInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "customer_phone_number": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "customer_shipping_address": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "customer_billing_address": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "line_item_1": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_2": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_3": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_4": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_5": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_6": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_7": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_8": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_9": TextInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "line_item_10": TextInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "shipping_charge": NumberInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            # "tax": NumberInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "total_due": NumberInput(attrs={"class": "blu_invoice_edit_field w-input"}),
            # "total_paid": NumberInput(
            #     attrs={"class": "blu_invoice_edit_field w-input"}
            # ),
            "visible_notes": Textarea(attrs={"rows": 4, "cols": 15}),
            "private_notes": Textarea(attrs={"rows": 4, "cols": 15}),
        }
