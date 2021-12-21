from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse

from core.group_permissions import get_permissions

from .forms import ProfileEditForm, UserCreationForm, UserEditForm
from .models import Profile


User = get_user_model()


@permission_required("can_add_user", raise_exception=True)
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            user = authenticate(
                username=request.POST["email"],
                user_type=request.POST["user_type"],
                password=request.POST["password1"],
            )
            # get the choose group and add this user
            user_type = request.POST["user_type"]
            try:
                group = Group.objects.get(name=user_type)
            except ObjectDoesNotExist:
                group = Group.objects.create(name=user_type)
                group.permissions.set(get_permissions(user_type))

            user.groups.add(group)

            # login(request, user)
            return redirect(reverse("core:home"))
    else:
        form = UserCreationForm()

    return render(request, "accounts/registration/signup.html", {"form": form})


# @permission_required("can_change_user", raise_exception=True)
# def edit_profile(request, author=None):
#     if request.method == "POST":
#         user_form = UserEditForm(instance=request.user, data=request.POST)
#         profile_form = ProfileEditForm(
#             instance=request.user.profile, data=request.POST, files=request.FILES,
#         )
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return redirect("user_profile", author=request.user)


@permission_required("can_change_user", raise_exception=True)
def edit_profile(request, user=None):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES,
        )
        if profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("/your_account/")
        else:
            return redirect("/your_account/")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        "accounts/profile_edit.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "User": User,
            "profile": Profile,
        },
    )
