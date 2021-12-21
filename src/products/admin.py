from django.contrib import admin

from core.admin_utils import admin_changelist_link, admin_link
from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter

from .models import Product, ProductCategory


class ProductCategoryAdmin(MPTTModelAdmin):
    mptt_indent_field = "name"
    list_display = [
        "name",
        # "parent",
        "created",
        "products_link",
        "related_products_count",
        "related_products_cumulative_count",
    ]
    list_display_links = ["name"]
    search_fields = ["name", "active"]
    list_per_page = 20
    # list_filter = ['name', 'created']
    # list_filter = [
    #     ('name', TreeRelatedFieldListFilter),
    # ]
    prepopulated_fields = {"slug": ("name",)}
    view_on_site = True

    @admin_changelist_link(
        "products", "Products", query_string=lambda c: "categories_id={}".format(c.pk),
    )
    def products_link(self, albums):
        return "Category products"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative albums count
        qs = ProductCategory.objects.add_related_count(
            qs, Product, "categories", "products_cumulative_count", cumulative=True,
        )

        # Add non cumulative albums count
        qs = ProductCategory.objects.add_related_count(
            qs, Product, "categories", "products_count", cumulative=False
        )
        return qs

    def related_products_count(self, instance):
        return instance.products_count

    related_products_count.short_description = "Nr. of products"

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count

    related_products_cumulative_count.short_description = "Nr. of products (in tree)"


admin.site.register(ProductCategory, ProductCategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "verbose_name",
        # "created",
        # "updated",
        "category_link",
        "image_tag",
    ]
    list_display_links = ["verbose_name"]
    list_select_related = ["categories"]
    list_filter = ["created", ("categories", TreeRelatedFieldListFilter)]
    prepopulated_fields = {"slug": ("verbose_name",)}
    list_per_page = 20
    show_full_result_count = False
    view_on_site = True
    date_hierarchy = "created"

    def get_queryset(self, request):
        return (
            super(ProductAdmin, self).get_queryset(request).select_related("categories")
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter the drop down showing prepopulated with the authenticated user"""
        if db_field.name == "author":
            kwargs["initial"] = request.user.id
        return super(ProductAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    @admin_link("categories", "categories")
    def category_link(self, category):
        """Url link for the categories of business."""
        """With 20000 products this decorator increases the list page load from 800 ms to ~3000 ms"""
        return category


admin.site.register(Product, ProductAdmin)
