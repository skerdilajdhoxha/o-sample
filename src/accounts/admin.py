from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .forms import UserChangeForm, UserCreationForm
from .models import Profile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "user_type",
                    "expiration_date",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2"),},),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "username", "image_tag"]


admin.site.register(Profile, ProfileAdmin)
