from django.contrib import admin

from core.admin_utils import admin_changelist_link, admin_link
from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter

from .models import Album, AlbumCategory, AlbumPhotos


class AlbumCategoryAdmin(MPTTModelAdmin):
    mptt_indent_field = "name"
    list_display = [
        "name",
        # "parent",
        "created",
        "albums_link",
        "related_albums_count",
        "related_albums_cumulative_count",
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
        "albums", "Albums", query_string=lambda c: "categories_id={}".format(c.pk),
    )
    def albums_link(self, albums):
        return "Category albums"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative albums count
        qs = AlbumCategory.objects.add_related_count(
            qs, Album, "categories", "albums_cumulative_count", cumulative=True
        )

        # Add non cumulative albums count
        qs = AlbumCategory.objects.add_related_count(
            qs, Album, "categories", "albums_count", cumulative=False
        )
        return qs

    def related_albums_count(self, instance):
        return instance.albums_count

    related_albums_count.short_description = "Nr. of albums"

    def related_albums_cumulative_count(self, instance):
        return instance.albums_cumulative_count

    related_albums_cumulative_count.short_description = "Nr. of albums (in tree)"


admin.site.register(AlbumCategory, AlbumCategoryAdmin)


class AlbumPhotosInline(admin.TabularInline):
    model = AlbumPhotos
    extra = 1


class AlbumAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ["name"]
    list_filter = ["created"]
    view_on_site = True
    inlines = [AlbumPhotosInline]


admin.site.register(Album, AlbumAdmin)
