from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from activity.utils import create_action

from .forms import (
    ProductCategoryCreateForm,
    ProductCategoryUpdateForm,
    ProductEditForm,
    ProductPhotosFormSet,
)
from .models import Product, ProductCategory


@permission_required("products.add_productcategory", raise_exception=True)
def create_category(request):
    last_object = ProductCategory.objects.order_by("-pk").first()
    form = ProductCategoryCreateForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.cat_nr = 1 if not last_object else int(last_object.cat_nr) + 1
        instance.save()
        create_action(request.user, "created category", instance, instance)
        return redirect("products:category_list")
    context = {
        "form": form,
    }
    return render(request, "products/category_create.html", context)


@permission_required("products.change_productcategory", raise_exception=True)
def category_edit(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    if request.method == "POST":
        form = ProductCategoryUpdateForm(
            instance=category, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            create_action(request.user, "updated category", instance, instance)
            return redirect(category.get_absolute_url())
        else:
            return redirect(category.get_absolute_url())
    else:
        form = ProductCategoryUpdateForm(instance=category)
    return render(
        request, "products/category_edit.html", {"form": form, "category": category},
    )


@permission_required("products.view_productcategory", raise_exception=True)
def categories(request):
    all_categories = ProductCategory.objects.order_by("cat_nr")
    return render(
        request, "products/category_list.html", {"categories": all_categories}
    )


@permission_required("products.view_productcategory", raise_exception=True)
def category_detail(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    products = category.products.prefetch_related("categories").order_by(
        "product_nr"
    )

    page = request.GET.get("page", 1)
    paginator = Paginator(products, 12)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    index = objects.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = paginator.page_range[start_index:end_index]
    context = {
        "object_list": objects,
        "page_range": page_range,
        "instance": category,
    }
    return render(request, "products/category_detail.html", context)


@permission_required("products.view_productcategory", raise_exception=True)
def move_cat_left(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    current_category = category.cat_nr
    previous_category = (
        ProductCategory.objects.filter(cat_nr__lt=category.cat_nr)
        .order_by("-cat_nr")
        .first()
    )
    if previous_category is not None:
        # change cat_nr for current category with previous category
        category_new = previous_category.cat_nr
        category.cat_nr = category_new

        # change previous category cat_nr with current category :)
        previous_category.cat_nr = current_category
        # save both category instances
        category.save()
        previous_category.save()
    else:
        pass
    return redirect("products:category_list")


@permission_required("products.view_productcategory", raise_exception=True)
def move_cat_right(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    current_category = category.cat_nr
    previous_category = (
        ProductCategory.objects.filter(cat_nr__gt=category.cat_nr)
        .order_by("cat_nr")
        .first()
    )
    if previous_category is not None:
        # change cat_nr for current category with previous category
        category_new = previous_category.cat_nr
        category.cat_nr = category_new

        # change previous category cat_nr with current category :)
        previous_category.cat_nr = current_category
        # save both category instances
        category.save()
        previous_category.save()
    else:
        pass
    return redirect("products:category_list")


@permission_required("products.delete_productcategory", raise_exception=True)
def category_delete(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    category.delete()
    create_action(request.user, "deleted category", category, category)
    return redirect("products:category_list")


@permission_required("products.view_product", raise_exception=True)
def product_list(request):
    products = Product.objects.prefetch_related("user", "categories").order_by(
        "product_nr"
    )
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 6)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    index = objects.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = paginator.page_range[start_index:end_index]
    context = {"object_list": products, "page_range": page_range}
    return render(request, "products/product_list.html", context)


@permission_required("products.change_product", raise_exception=True)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        form = ProductEditForm(instance=product, data=request.POST, files=request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            create_action(request.user, "updated category", instance)
            return redirect(product.get_absolute_url())
        else:
            return redirect(product.get_absolute_url())
    else:
        form = ProductEditForm(instance=product)
    context = {"product": product, "form": form}
    return render(request, "products/product_detail.html", context)


@permission_required("products.delete_product")
def product_delete(request, slug, slug2):
    product = get_object_or_404(Product, slug=slug)
    category = get_object_or_404(ProductCategory, slug=slug2)
    product.delete()
    create_action(request.user, "deleted product", product, product)
    return redirect("products:category_detail", slug=category.slug)


class ProductCreate(PermissionRequiredMixin, CreateView):
    permission_required = "products.add_product"
    model = Product
    fields = [
        "verbose_name",
        "sku",
        # "categories",
        "suggest_retail_price",
        "production_cost",
        "tier_1_vendor_price",
        "tier_2_vendor_price",
        "tier_3_vendor_price",
        "shipping_weight",
        "shipping_box_length",
        "shipping_box_depth",
        "shipping_box_height",
        "uline_box",
        "product_weight",
        "product_length",
        "product_depth",
        "product_height",
    ]
    template_name = "products/product_create_or_update.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the `ProductCategory` instance exists
        before going any further.
        """
        last_object = Product.objects.order_by("-pk").first()
        self.product_nr = (
            1 if not last_object else int(last_object.product_nr) + 1
        )
        self.categories = get_object_or_404(ProductCategory, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(ProductCreate, self).get_context_data(**kwargs)
        data["categories"] = self.categories
        if self.request.POST:
            data["photos"] = ProductPhotosFormSet(self.request.POST, self.request.FILES)
        else:
            data["photos"] = ProductPhotosFormSet()
        return data

    def form_valid(self, form):
        last_object = Product.objects.order_by("-pk").first()
        context = self.get_context_data()
        photos = context["photos"]
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.categories = self.categories
            # if it's first object product_nr 1 else last product_nr + 1
            self.object.product_nr = (
                1 if not last_object else int(last_object.product_nr) + 1
            )
            self.object = form.save()
            if photos.is_valid():
                photos.instance = self.object
                photos.save()
                create_action(
                    self.request.user, "created product", self.object, self.object,
                )
        return super(ProductCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "products:category_detail", kwargs={"slug": self.categories.slug}
        )


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "products.change_product"
    model = Product
    fields = [
        "verbose_name",
        "sku",
        "categories",
        "suggest_retail_price",
        "production_cost",
        "tier_1_vendor_price",
        "tier_2_vendor_price",
        "tier_3_vendor_price",
        "shipping_weight",
        "shipping_box_length",
        "shipping_box_depth",
        "shipping_box_height",
        "uline_box",
        "product_weight",
        "product_length",
        "product_depth",
        "product_height",
    ]
    template_name = "products/product_create_or_update.html"

    def get_context_data(self, **kwargs):
        data = super(ProductUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["photos"] = ProductPhotosFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            data["photos"] = ProductPhotosFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photos = context["photos"]
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object = form.save()
            if photos.is_valid():
                photos.instance = self.object
                photos.save()
                create_action(
                    self.request.user, "updated product", self.object, self.object,
                )
        return super(ProductUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "products:category_detail", kwargs={"slug": self.object.categories.slug}
        )


@permission_required("products.change_product", raise_exception=True)
def move_product_left(request, cat_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    # category = get_object_or_404(ProductCategory, slug=cat_slug)
    current_product = product.product_nr
    previous_product = (
        Product.objects.filter(product_nr__lt=product.product_nr)
        .order_by("-product_nr")
        .first()
    )
    if previous_product is not None:
        # change product_nr for current product with previous product
        product_new = previous_product.product_nr
        product.product_nr = product_new

        # change previous product product_nr with current product :)
        previous_product.product_nr = current_product
        # save both product instances
        product.save()
        previous_product.save()
    else:
        pass
    # return redirect("products:product_list")
    return redirect("products:category_detail", slug=cat_slug)


@permission_required("products.change_product", raise_exception=True)
def move_product_right(request, cat_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    # category = get_object_or_404(ProductCategory, slug=cat_slug)
    current_product = product.product_nr
    previous_product = (
        Product.objects.filter(product_nr__gt=product.product_nr)
        .order_by("product_nr")
        .first()
    )
    if previous_product is not None:
        # change product_nr for current product with previous product
        product_new = previous_product.product_nr
        product.product_nr = product_new

        # change previous product product_nr with current product :)
        previous_product.product_nr = current_product
        # save both product instances
        product.save()
        previous_product.save()
    else:
        pass
    # return redirect("products:product_list")
    return redirect("products:category_detail", slug=cat_slug)
