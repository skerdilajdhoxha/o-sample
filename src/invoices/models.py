from django.conf import settings
from django.db import models
from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel
from products.models import Product


class Invoice(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_invoices"
    )
    invoice_title = models.CharField(max_length=200)
    # invoice_nr will be used for changing positions, can change
    invoice_nr = models.PositiveIntegerField(null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name="invoices")
    # invoice_number will get it's value from primary key, can not change
    invoice_number = models.CharField(max_length=200, null=True, blank=True)
    customer_company_name = models.CharField(max_length=200, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone_number = models.CharField(max_length=200, null=True, blank=True)
    customer_shipping_address = models.CharField(max_length=200, null=True, blank=True)
    customer_billing_address = models.CharField(max_length=200, null=True, blank=True)
    line_item_1 = models.CharField(max_length=200, null=True, blank=True)
    line_item_2 = models.CharField(max_length=200, null=True, blank=True)
    line_item_3 = models.CharField(max_length=200, null=True, blank=True)
    line_item_4 = models.CharField(max_length=200, null=True, blank=True)
    line_item_5 = models.CharField(max_length=200, null=True, blank=True)
    line_item_6 = models.CharField(max_length=200, null=True, blank=True)
    line_item_7 = models.CharField(max_length=200, null=True, blank=True)
    line_item_8 = models.CharField(max_length=200, null=True, blank=True)
    line_item_9 = models.CharField(max_length=200, null=True, blank=True)
    line_item_10 = models.CharField(max_length=200, null=True, blank=True)
    shipping_charge = models.DecimalField(
        decimal_places=2, max_digits=50, null=True, blank=True
    )
    tax = models.DecimalField(decimal_places=2, max_digits=50, null=True, blank=True)
    total_due = models.DecimalField(
        decimal_places=2, max_digits=50, null=True, blank=True
    )
    total_paid = models.DecimalField(
        decimal_places=2, max_digits=50, null=True, blank=True
    )
    visible_notes = models.TextField(null=True, blank=True)
    private_notes = models.TextField(null=True, blank=True)

    slug = models.SlugField(unique=True)

    pdf = models.FileField(upload_to="invoices/pdfs/", null=True, blank=True)
    image = models.ImageField(upload_to="invoices/images/", null=True, blank=True)

    def __str__(self):
        return self.invoice_title

    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse("invoices:invoice_detail", kwargs={"slug": self.slug})

    def get_pdf_url(self):
        return reverse("invoices:invoice_pdf", kwargs={"pk": self.pk})

    def get_unique_slug(self):
        """Changes the slug if 2 or more objects are created with the same title"""
        slug = slugify(self.invoice_title)
        unique_slug = slug
        num = 1
        while Invoice.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        """Change slug if you change the title"""
        slug = slugify(self.invoice_title)
        if self.slug != slug:
            self.slug = slug

            if self.slug:
                self.slug = self.get_unique_slug()
        super(Invoice, self).save()
