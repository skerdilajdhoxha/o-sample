from django.urls import path

from . import views


app_name = "invoices"

urlpatterns = [
    path("", views.invoice_list, name="invoice_list"),
    path("create/", views.invoice_create, name="invoice_create"),
    path("<slug:slug>/", views.invoice_detail, name="invoice_detail"),
    path("<slug:slug>/update/", views.invoice_update, name="invoice_update"),
    path("<slug:slug>/delete/", views.invoice_delete, name="invoice_delete"),
    path("<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    # path("<int:pk>/pdf2/", views.generatepdf, name="generatepdf"),
    path("<int:pk>/left/", views.move_left, name="left"),
    path("<int:pk>/right/", views.move_right, name="right"),
    path("<int:pk>/pdf_download/", views.DownloadPDF.as_view(), name="pdf_download",),
]
