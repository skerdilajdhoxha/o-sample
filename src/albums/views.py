from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from activity.utils import create_action

from .forms import AlbumCategoryCreateForm, AlbumCategoryUpdateForm, AlbumPhotosFormSet
from .models import Album, AlbumCategory


@permission_required("albums.add_albumcategory", raise_exception=True)
def create_category(request):
    last_object = AlbumCategory.objects.order_by("-pk").first()
    form = AlbumCategoryCreateForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.cat_nr = 1 if not last_object else int(last_object.cat_nr) + 1
        instance.save()
        create_action(request.user, "created category", instance, instance)
        return redirect("albums:category_list")
    context = {
        "form": form,
    }
    return render(request, "albums/category_create.html", context)


@permission_required("albums.change_albumcategory", raise_exception=True)
def category_edit(request, slug):
    category = get_object_or_404(AlbumCategory, slug=slug)
    if request.method == "POST":
        form = AlbumCategoryUpdateForm(
            instance=category, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            create_action(request.user, "modified category", instance, instance)
            return redirect(category.get_absolute_url())
        else:
            return redirect(category.get_absolute_url())
    else:
        form = AlbumCategoryUpdateForm(instance=category)
    return render(
        request, "albums/category_edit.html", {"form": form, "category": category},
    )


@permission_required("albums.view_albumcategory", raise_exception=True)
def categories(request):
    all_categories = AlbumCategory.objects.order_by("cat_nr")
    return render(request, "albums/category_list.html", {"categories": all_categories})


@permission_required("albums.view_albumcategory", raise_exception=True)
def category_detail(request, slug):
    category = get_object_or_404(AlbumCategory, slug=slug)
    albums = category.albums.prefetch_related("categories").all()

    context = {"object_list": albums, "instance": category}
    return render(request, "albums/category_detail.html", context)


@permission_required("albums.delete_albumcategory", raise_exception=True)
def category_delete(request, slug):
    category = get_object_or_404(AlbumCategory, slug=slug)
    category.delete()
    create_action(request.user, "deleted category", category, category)
    return redirect("albums:category_list")


@permission_required("albums.view_albumcategory", raise_exception=True)
def move_cat_left(request, slug):
    category = get_object_or_404(AlbumCategory, slug=slug)
    current_category = category.cat_nr
    previous_category = (
        AlbumCategory.objects.filter(cat_nr__lt=category.cat_nr)
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
    return redirect("albums:category_list")


@permission_required("albums.view_albumcategory", raise_exception=True)
def move_cat_right(request, slug):
    category = get_object_or_404(AlbumCategory, slug=slug)
    current_category = category.cat_nr
    previous_category = (
        AlbumCategory.objects.filter(cat_nr__gt=category.cat_nr)
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
    return redirect("albums:category_list")


class AlbumList(PermissionRequiredMixin, ListView):
    permission_required = "albums.view_album"
    model = Album
    template_name = "albums/album_list.html"
    paginate_by = 9
    context_object_name = "object_list"

    def get_context_data(self, *args, **kwargs):
        # products = Album.objects.prefetch_related("photos").all()
        albums = Album.objects.select_related("categories").order_by("album_nr")

        page = self.request.GET.get("page", 1)
        paginator = Paginator(albums, 6)
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
        context = {"object_list": objects, "page_range": page_range}
        return context


class AlbumCreate(PermissionRequiredMixin, CreateView):
    permission_required = "albums.add_album"
    model = Album
    fields = ["name", "categories", "description"]
    template_name = "albums/album_create_or_update.html"

    def get_context_data(self, **kwargs):
        data = super(AlbumCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["photos"] = AlbumPhotosFormSet(self.request.POST, self.request.FILES)
        else:
            data["photos"] = AlbumPhotosFormSet()
        return data

    def form_valid(self, form):
        last_object = Album.objects.order_by("-pk").first()
        context = self.get_context_data()
        photos = context["photos"]
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            # if it's first object album_nr 1 else last album_nr + 1
            self.object.album_nr = (
                1 if not last_object else int(last_object.album_nr) + 1
            )
            self.object = form.save()
            if photos.is_valid():
                photos.instance = self.object
                photos.save()
                create_action(
                    self.request.user, "created album", self.object, self.object,
                )
        return super(AlbumCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("albums:detail", kwargs={"pk": self.object.pk})


class AlbumUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "albums.change_album"
    model = Album
    fields = ["name", "categories", "description"]
    template_name = "albums/album_create_or_update.html"

    def get_context_data(self, **kwargs):
        data = super(AlbumUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["photos"] = AlbumPhotosFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            data["photos"] = AlbumPhotosFormSet(instance=self.object)
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
                    self.request.user, "modified album", self.object, self.object,
                )
        return super(AlbumUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("albums:detail", kwargs={"pk": self.object.pk})


class AlbumDetail(PermissionRequiredMixin, DetailView):
    permission_required = "albums.view_album"
    model = Album
    template_name = "albums/album_detail.html"
    context_object_name = "album"


class AlbumDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "albums.delete_album"
    model = Album
    success_url = reverse_lazy("albums:list")

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.success_url
        self.object.delete()
        create_action(request.user, "deleted album", self.object, self.object)
        return HttpResponseRedirect(success_url)


@permission_required("albums.change_album", raise_exception=True)
def move_album_left(request, pk):
    album = get_object_or_404(Album, pk=pk)
    current_album = album.album_nr
    previous_album = (
        Album.objects.filter(album_nr__lt=album.album_nr).order_by("-album_nr").first()
    )
    if previous_album is not None:
        # change album_nr for current album with previous album
        album_new = previous_album.album_nr
        album.album_nr = album_new

        # change previous album album_nr with current album :)
        previous_album.album_nr = current_album
        # save both album instances
        album.save()
        previous_album.save()
    else:
        pass
    return redirect("albums:list")


@permission_required("albums.change_album", raise_exception=True)
def move_album_right(request, pk):
    album = get_object_or_404(Album, pk=pk)
    current_album = album.album_nr
    previous_album = (
        Album.objects.filter(album_nr__gt=album.album_nr).order_by("album_nr").first()
    )
    if previous_album is not None:
        # change album_nr for current album with previous album
        album_new = previous_album.album_nr
        album.album_nr = album_new

        # change previous album album_nr with current album :)
        previous_album.album_nr = current_album
        # save both album instances
        album.save()
        previous_album.save()
    else:
        pass
    return redirect("albums:list")
