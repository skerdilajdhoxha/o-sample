from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class AlbumCategory(MPTTModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    cat_nr = models.PositiveIntegerField(null=True, blank=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
    )
    photo = models.ImageField(
        upload_to="albums/categories/", default="profiles/image-coming-soon.jpg",
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        unique_together = ("parent", "slug")
        verbose_name = "Album Category"
        verbose_name_plural = "Album Categories"

    # def get_slug_list(self):
    #     try:
    #         ancestors = self.get_ancestors(include_self=True)
    #     except:
    #         ancestors = []
    #     else:
    #         ancestors = [i.slug for i in ancestors]
    #     slugs = []
    #     for i in range(len(ancestors)):
    #         slugs.append("/".join(ancestors[: i + 1]))
    #     return slugs

    def get_absolute_url(self):
        return reverse("albums:category_detail", kwargs={"slug": self.slug})

    def _get_unique_slug(self):
        """Changes the slug if 2 or more objects are created with the same title"""
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while AlbumCategory.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        """Change slug if you change the title"""
        slug = slugify(self.name)
        if self.slug != slug:
            self.slug = slug
            # change the slug if if there's another instance with this slug
            if self.slug:
                self.slug = self._get_unique_slug()
        super(AlbumCategory, self).save()


class Album(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_albums"
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    album_nr = models.PositiveIntegerField(null=True, blank=True)
    categories = models.ForeignKey(
        AlbumCategory, on_delete=models.PROTECT, related_name="albums",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse("albums:detail", kwargs={"pk": self.pk})

    def get_first_photo(self):
        img = self.photos.last()
        if img:
            return img.photo.url
        if not img:
            return "/media/profiles/image-coming-soon.jpg"

    def all_photos(self):
        return self.photos.all()


def image_upload_to(instance, filename):
    name = instance.album
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s.%s" % (slugify(basename), file_extension)
    return "albums/%s/%s" % (slug, new_filename)


class AlbumPhotos(TimeStampedModel):
    photo = models.ImageField(
        upload_to=image_upload_to, default="profiles/image-coming-soon.jpg"
    )
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")

    def __str__(self):
        return self.photo.name

    class Meta:
        ordering = ["-created"]
