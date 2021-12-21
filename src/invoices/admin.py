from django.contrib import admin

from .models import Invoice


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_title", "user", "created", "modified"]
    list_filter = ["created"]
    prepopulated_fields = {"slug": ("invoice_title",)}
    view_on_site = True


admin.site.register(Invoice, InvoiceAdmin)
