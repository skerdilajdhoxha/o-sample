from django.urls import path
from django.views.generic import TemplateView

from . import views


app_name = "core"

urlpatterns = [
    path("", views.home_page, name="home"),
    path(
        "logged_out/",
        TemplateView.as_view(template_name="core/logged_out.html"),
        name="logged_out",
    ),
]
