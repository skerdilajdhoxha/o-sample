from django.contrib.sites.models import Site


def site_url(request):
    return {
        "site": Site.objects.get_current(),
        "protocol": request.is_secure() and "https" or "http",
        "request": request,
    }
