from django.urls import path

from . import views


app_name = "members"

urlpatterns = [
    path("", views.all_members, name="member_list"),
    path(
        "<int:pk>/change_password/",
        views.edit_member_password,
        name="edit_member_password",
    ),
    path("<int:pk>/", views.edit_profile, name="member_profile"),
]
