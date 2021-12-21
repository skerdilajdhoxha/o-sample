import os
import tempfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files import File
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from activity.utils import create_action
from core.helpers import increment_account_number, render_to_pdf
from pdf2image import convert_from_path

from .forms import InvoiceCreateForm, InvoiceUpdateForm
from .models import Invoice


User = get_user_model()


@permission_required("invoices.add_invoice", raise_exception=True)
def invoice_create(request):
    last_object = Invoice.objects.order_by("-pk").first()

    form = InvoiceCreateForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        # first save the invoice object
        instance = form.save(commit=False)
        instance.user = request.user
        # if any objects exists, last_obj.invoice_nr + 1, else invoice_nr 1
        instance.invoice_nr = 1 if not last_object else int(last_object.invoice_nr) + 1
        if last_object is None:
            instance.invoice_number = "BLU-00001"
        else:
            instance.invoice_number = increment_account_number()
        instance.save()

        create_action(request.user, "created invoice", instance, instance)
        # save the pdf field from the object fields
        context = {
            "invoice": instance,
        }
        pdf = render_to_pdf("invoices/invoice.html", context)
        filename = f"Invoice_{instance.slug}.pdf"
        a = instance.pdf.save(filename, File(BytesIO(pdf.content)))
        # print(a)

        # save image from first page of pdf file
        filename = instance.pdf.path
        with tempfile.TemporaryDirectory() as path:
            images_from_path = convert_from_path(
                filename, 100, output_folder=path, last_page=1, first_page=0
            )
        base_filename = os.path.splitext(os.path.basename(filename))[0] + ".jpg"
        save_dir = os.path.join(settings.MEDIA_ROOT, "invoices/images/")
        for page in images_from_path:
            page.save(os.path.join(save_dir, base_filename), "JPEG")

            instance.image = "{}".format(
                os.path.join("invoices/images/", base_filename)
            )
            instance.save()

        return redirect("invoices:invoice_list")

    context = {
        "form": form,
    }
    return render(request, "invoices/invoice_create.html", context)


@permission_required("invoices.view_invoice", raise_exception=True)
def invoice_list(request):
    invoices = Invoice.objects.all().order_by("invoice_nr")

    page = request.GET.get("page", 1)
    paginator = Paginator(invoices, 6)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    index = objects.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = paginator.page_range[start_index:end_index]
    context = {"object_list": objects, "page_range": page_range}

    return render(request, "invoices/invoice_list.html", context)


@permission_required("invoices.view_invoice", raise_exception=True)
def invoice_detail(request, slug=None):
    invoice = get_object_or_404(Invoice, slug=slug)
    context = {
        "invoice": invoice,
    }
    return render(request, "invoices/invoice_detail.html", context)


@permission_required("invoices.change_invoice", raise_exception=True)
def invoice_update(request, slug):
    invoice = get_object_or_404(Invoice, slug=slug)
    if request.method == "POST":
        form = InvoiceUpdateForm(
            instance=invoice, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            create_action(request.user, "updated invoice", instance, instance)

            # save the pdf field from the object fields
            context = {
                "invoice": instance,
            }
            pdf = render_to_pdf("invoices/invoice.html", context)
            filename = f"Invoice_{instance.slug}.pdf"
            a = instance.pdf.save(filename, File(BytesIO(pdf.content)))
            # print(a)

            # save image from first page of pdf file
            filename = instance.pdf.path
            with tempfile.TemporaryDirectory() as path:
                images_from_path = convert_from_path(
                    filename, 100, output_folder=path, last_page=1, first_page=0,
                )
            base_filename = os.path.splitext(os.path.basename(filename))[0] + ".jpg"
            save_dir = os.path.join(settings.MEDIA_ROOT, "invoices/images/")
            for page in images_from_path:
                page.save(os.path.join(save_dir, base_filename), "JPEG")

                instance.image = "{}".format(
                    os.path.join("invoices/images/", base_filename)
                )
                instance.save()

            return redirect("invoices:invoice_list")
        else:
            return redirect(invoice.get_absolute_url())
    else:
        form = InvoiceUpdateForm(instance=invoice)
    return render(
        request, "invoices/invoice_update.html", {"form": form, "invoice": invoice},
    )


@permission_required("invoices.delete_invoice", raise_exception=True)
def invoice_delete(request, slug):
    invoice = get_object_or_404(Invoice, slug=slug)
    invoice.delete()
    create_action(request.user, "deleted invoice", invoice, invoice)
    return redirect("invoices:invoice_list")


@permission_required("invoices.view_invoice", raise_exception=True)
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {
        "invoice": invoice,
    }
    pdf = render_to_pdf("invoices/invoice.html", context)
    filename = f"Invoice_{invoice.slug}.pdf"
    if invoice.pdf is None:
        invoice.pdf.save(filename, File(BytesIO(pdf.content)))
    else:
        pass
    return HttpResponse(pdf, content_type="application/pdf")


# @receiver(pre_save, sender=Invoice)
# def generate_obj_pdf(sender, instance, *args, **kwargs):
#     """Saves a pdf file with the data given to the template"""
#     context = {'invoices': instance}
#     pdf = render_to_pdf('invoices/invoice.html', context)
#     filename = f"Invoice_{instance.slug}.pdf"
#     instance.pdf.save(filename, File(BytesIO(pdf.content)))


class DownloadPDF(PermissionRequiredMixin, View):
    permission_required = "invoices.view_invoice"

    def get(self, request, pk, **kwargs):
        invoice = get_object_or_404(Invoice, pk=pk)
        context = {
            "invoice": invoice,
        }
        pdf = render_to_pdf("invoices/invoice.html", context)

        response = HttpResponse(pdf, content_type="application/pdf")
        filename = f"Invoice_{invoice.slug}.pdf"
        content = "attachment; filename='%s'" % filename
        response["Content-Disposition"] = content
        return response


# @login_required
# def generatepdf(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     response = HttpResponse(content_type="application/pdf")
#     response['Content-Disposition'] = "inline; filename={date}-{name}-invoices.pdf".format(
#         date=invoice.created.strftime('%Y-%m-%d_%H:%m'),
#         name=slugify(invoice.invoice_title),
#     )
#     html = render_to_string("invoices/invoice_pdf.html", {
#         'invoices': invoice,
#     })
#
#     font_config = FontConfiguration()
#     HTML(string=html).write_pdf(response, font_config=font_config)
#     return response


@permission_required("invoices.change_invoice", raise_exception=True)
def move_left(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    current_invoice = invoice.invoice_nr

    previous_invoice = (
        Invoice.objects.filter(invoice_nr__lt=invoice.invoice_nr)
        .order_by("-invoice_nr")
        .first()
    )
    if previous_invoice is not None:
        # change invoice_nr for current invoice with previous invoice
        invoice_new = previous_invoice.invoice_nr
        invoice.invoice_nr = invoice_new

        # change previous invoice invoice_nr with current invoice :)
        previous_invoice.invoice_nr = current_invoice
        # save both invoice instances
        invoice.save()
        previous_invoice.save()
    else:
        pass
    return redirect("invoices:invoice_list")


@permission_required("invoices.change_invoice", raise_exception=True)
def move_right(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    current_invoice = invoice.invoice_nr

    previous_invoice = (
        Invoice.objects.filter(invoice_nr__gt=invoice.invoice_nr)
        .order_by("invoice_nr")
        .first()
    )
    if previous_invoice is not None:
        # change invoice_nr for current invoice with previous invoice
        invoice_new = previous_invoice.invoice_nr
        invoice.invoice_nr = invoice_new

        # change previous invoice invoice_nr with current invoice :)
        previous_invoice.invoice_nr = current_invoice
        # save both invoice instances
        invoice.save()
        previous_invoice.save()
    else:
        pass
    return redirect("invoices:invoice_list")
