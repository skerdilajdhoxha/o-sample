from django.urls import path

from . import views


app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("categories/", views.categories, name="category_list"),
    path(
        "category/<slug:slug>/create-product/",
        views.ProductCreate.as_view(),
        name="product_create",
    ),
    path("category/create/", views.create_category, name="category_create"),
    path("category/<slug:slug>/left/", views.move_cat_left, name="category_left"),
    path("category/<slug:slug>/right/", views.move_cat_right, name="category_right",),
    path(
        "<slug:slug>/update-product/",
        views.ProductUpdate.as_view(),
        name="product_edit",
    ),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
    path(
        "<slug:slug>/<slug:slug2>/delete/", views.product_delete, name="product_delete"
    ),
    path(
        "category/<slug:cat_slug>/<slug:slug>/left/",
        views.move_product_left,
        name="product_left",
    ),
    path(
        "category/<slug:cat_slug>/<slug:slug>/right/",
        views.move_product_right,
        name="product_right",
    ),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("category/<slug:slug>/update/", views.category_edit, name="category_edit",),
    path("<slug:slug>/delete/", views.category_delete, name="category_delete",),
]
