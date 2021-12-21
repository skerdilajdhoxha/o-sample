from __future__ import unicode_literals

from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Define a model manager for User model with email instead of username field."""

    use_in_migrations = True

    def _create_user(self, email, user_type, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user_type = self.model.normalize_username(user_type)
        user = self.model(email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, user_type, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, user_type, password, **extra_fields)

    def create_superuser(self, email, user_type, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, user_type, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    SUPER_USER = "super_user"
    BLU_ADMIN = "blu_admin"
    OHI_ADMIN = "ohi_admin"
    BLU_USER = "blu_user"
    OHI_USER = "ohi_user"
    GENERAL_USER = "general_user"
    USER_TYPE = (
        (SUPER_USER, "Super user"),
        (BLU_ADMIN, "Blu admin"),
        (OHI_ADMIN, "Ohi admin"),
        (BLU_USER, "Blu user"),
        (OHI_USER, "Ohi user"),
        (GENERAL_USER, "general user"),
    )
    user_type = models.CharField(max_length=32, choices=USER_TYPE, default=GENERAL_USER)

    EXPIRED = "expired"
    ONE_WEEK = date.today() + timedelta(days=7)
    ONE_MONTH = date.today() + timedelta(days=30)
    ONE_YEAR = date.today() + timedelta(days=365)
    ENDLESSLY = "endlessly"
    EXPIRATION_DATE = (
        (EXPIRED, "Expired"),
        (str(date.today() + timedelta(days=7)), "One week"),
        (str(date.today() + timedelta(days=30)), "One month"),
        (str(date.today() + timedelta(days=365)), "One year"),
        (ENDLESSLY, "Endlessly"),
    )
    expiration_date = models.CharField(
        max_length=150, choices=EXPIRATION_DATE, default=ENDLESSLY
    )
    email = models.EmailField(_("email address"), unique=True, null=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_type"]
    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(
        blank=True, null=True, help_text="Should be entered, year-month-day"
    )
    photo = models.ImageField(
        upload_to="profiles/", default="profiles/image-coming-soon.jpg"
    )

    def __str__(self):
        return "Profile for user {}".format(self.user.email)

    def get_absolute_url(self):
        return reverse("user_profile", kwargs={"pk": self.pk})

    def photo_url(self):
        """Returns URL of the photo or a default one if object doesn't have one."""
        if self.photo:
            return self.photo.url
        else:
            return "/static/ohi-shop/images/image-coming-soon.jpg"

    def image_tag(self):
        """Returns URL of the photo or a default one if object doesn't have one.Used for admin"""
        if self.photo:
            return mark_safe(
                '<img src="%s" style="max-width: 60px; max-height:60px;" />'
                % self.photo.url
            )
        else:
            return "No image"

    image_tag.short_description = "Photo"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()
