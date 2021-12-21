from copy import copy
from io import BytesIO

from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.template.loader import get_template

from invoices.models import Invoice
from xhtml2pdf import pisa


def increment_account_number():
    """
    Get the second last created user profile account number "2357-0051",
    the last one will be the one you're creating. Profiles are created automatically.
    Get the number from the second part and increment it by one.
    Or if profile account number is empty, get a number from 10 to 100
    """
    # profiles = Profile.objects.exclude(user__is_superuser=True)
    # last_profile = profiles.order_by('-pk')[1]
    last_object = Invoice.objects.order_by("-pk").first()
    if last_object.invoice_number != "":
        # nr = int(last_object.account_number[5:]) + 1
        # add the first part of the account number
        if len(str(last_object.pk)) == 1:
            final_nr = "BLU-0000" + str(last_object.pk)
        elif len(str(last_object.pk)) == 2:
            final_nr = "BLU-000" + str(last_object.pk)
        elif len(str(last_object.pk)) == 3:
            final_nr = "BLU-00" + str(last_object.pk)
        elif len(str(last_object.pk)) == 4:
            final_nr = "BLU-0" + str(last_object.pk)
        else:
            final_nr = "BLU-" + str(last_object.pk)
    else:
        final_nr = "BLU-00001"

    return final_nr


def update_field(field, obj):
    """
    Updates request's POST dictionary with values from object, for update purposes
    ModelField tries to override the fields that were not passed in the POST request with None,
    leading to loss of data
    """
    field = copy(field)
    for k, v in model_to_dict(obj).items():
        if k not in field:
            field[k] = v
    return field


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None
