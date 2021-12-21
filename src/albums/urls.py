from django.urls import path

from . import views


app_name = "albums"

urlpatterns = [
    path("", views.AlbumList.as_view(), name="list"),
    path("categories/", views.categories, name="category_list"),
    path("create/", views.AlbumCreate.as_view(), name="create"),
    path("category/create/", views.create_category, name="category_create"),
    path("category/<slug:slug>/left/", views.move_cat_left, name="category_left"),
    path("category/<slug:slug>/right/", views.move_cat_right, name="category_right",),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("category/<slug:slug>/update/", views.category_edit, name="category_edit",),
    path(
        "category/<slug:slug>/delete/", views.category_delete, name="category_delete",
    ),
    path("<int:pk>/", views.AlbumDetail.as_view(), name="detail"),
    path("<int:pk>/left/", views.move_album_left, name="album_left"),
    path("<int:pk>/right/", views.move_album_right, name="album_right"),
    path("<int:pk>/update/", views.AlbumUpdate.as_view(), name="update"),
    path("<int:pk>/delete/", views.AlbumDelete.as_view(), name="delete"),
]
