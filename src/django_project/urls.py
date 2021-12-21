"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView


urlpatterns = [
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path("not_my_admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("activity/", include("activity.urls")),
    path("members/", include("members.urls")),
    path("albums/", include("albums.urls", namespace="albums")),
    path("invoices/", include("invoices.urls", namespace="invoices")),
    path("products/", include("products.urls", namespace="products")),
    path("", include("core.urls", namespace="core")),
    # re_path(r'^.*', TemplateView.as_view(template_name='core/404.html'), name="404"),
    re_path(
        r"^(?!static) | (?!media).*",
        TemplateView.as_view(template_name="core/404.html"),
        name="404",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_title = "OHI SHOP"
admin.site.site_header = "OHI SHOP Admin"
admin.site.index_title = "OHI SHOP Models"
