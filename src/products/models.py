from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from core.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


# from invoices.models import Invoice


class ProductCategory(MPTTModel, TimeStampedModel):
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
        upload_to="products/categories/", default="profiles/image-coming-soon.jpg",
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        unique_together = ("parent", "slug")
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

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
        return reverse("products:category_detail", kwargs={"slug": self.slug})

    def _get_unique_slug(self):
        """Changes the slug if 2 or more objects are created with the same name"""
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while ProductCategory.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        """Change slug if you change the name"""
        slug = slugify(self.name)
        if self.slug != slug:
            self.slug = slug
            # change the slug if if there's another instance with this slug
            if self.slug:
                self.slug = self._get_unique_slug()
        super(ProductCategory, self).save()


class Product(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_products"
    )
    # invoices = models.ManyToManyField(Invoice, blank=True, related_name='products')

    verbose_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=200, blank=True, null=True)
    suggest_retail_price = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    production_cost = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    tier_1_vendor_price = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    tier_2_vendor_price = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    tier_3_vendor_price = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    shipping_weight = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name="shipping weight (lb)",
    )
    shipping_box_length = models.CharField(
        max_length=256, blank=True, null=True, verbose_name="shipping box length (inch)"
    )
    shipping_box_depth = models.CharField(
        max_length=256, blank=True, null=True, verbose_name="shipping box depth (inch)"
    )
    shipping_box_height = models.CharField(
        max_length=256, blank=True, null=True, verbose_name="shipping box height (inch)"
    )
    uline_box = models.CharField(max_length=256, blank=True, null=True)
    product_weight = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name="product weight (lb)",
    )
    product_length = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name="product length (inch)",
    )
    product_depth = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name="product depth (inch)",
    )
    product_height = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name="product height (inch)",
    )

    # photo = ProcessedImageField(upload_to=image_upload_to,
    #                             processors=[ResizeToFit(1000, 1000)],
    #                             format='JPEG',
    #                             options={'quality': 75})
    product_nr = models.PositiveIntegerField(default=1)
    slug = models.SlugField(unique=True)
    categories = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products",
    )

    def __str__(self):
        return self.verbose_name

    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    def get_first_photo(self):
        img = self.photos.last()
        if img:
            return img.photo.url
        if not img:
            return "/media/profiles/image-coming-soon.jpg"

    def all_photos(self):
        return self.photos.all()

    def image_tag(self):
        if self.get_first_photo():
            return mark_safe(
                '<img src="%s" style="max-width: 60px; max-height:60px;" />'
                % self.get_first_photo()
            )
        else:
            return "No Image"

    image_tag.short_description = "Photo"

    def get_unique_slug(self):
        """Changes the slug if 2 or more objects are created with the same verbose_name"""
        slug = slugify(self.verbose_name)
        unique_slug = slug
        num = 1
        while Product.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        """Change slug if you change the verbose_name"""
        slug = slugify(self.verbose_name)
        if self.slug != slug:
            self.slug = slug

            if self.slug:
                self.slug = self.get_unique_slug()
        super(Product, self).save()


def image_upload_to(instance, filename):
    name = instance.product
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s.%s" % (slugify(basename), file_extension)
    return "products/%s/%s" % (slug, new_filename)


class ProductPhotos(TimeStampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="photos"
    )
    photo = models.ImageField(
        upload_to=image_upload_to, default="profiles/image-coming-soon.jpg"
    )

    def __str__(self):
        return self.photo.verbose_name

    class Meta:
        ordering = ["-created"]
