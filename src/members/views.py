from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChangePasswordForm, ProfileUsernameEditForm, UserTypeEditForm

User = get_user_model()


@permission_required("view_user", raise_exception=True)
def all_members(request):
    members = User.objects.select_related("profile")
    return render(request, "members/member_list.html", {"object_list": members})


@permission_required("change_user", raise_exception=True)
def edit_member_password(request, pk=None):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = ChangePasswordForm(data=request.POST)
        if form.is_valid():
            # form.save()
            new_password = form.cleaned_data.get("new_password")
            user.set_password(new_password)
            user.save()
            return redirect("members:member_profile", pk=user.pk)
        else:
            return redirect("members:member_profile", pk=user.pk)
    else:
        form = ChangePasswordForm()
    return render(request, "members/password_change.html", {"form": form,},)


@permission_required("change_user", raise_exception=True)
def edit_profile(request, pk=None):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user_form = UserTypeEditForm(
            instance=user, data=request.POST, prefix="user_type_input"
        )
        profile_username_form = ProfileUsernameEditForm(
            instance=user.profile,
            data=request.POST,
            files=request.FILES,
            prefix="username_input",
        )

        if user_form.is_valid():
            instance = user_form.save(commit=False)
            expiration_date = user_form.cleaned_data.get("expiration_date")
            if expiration_date != "expired":
                instance.is_active = True
            else:
                instance.is_active = False
            instance.save()
        elif profile_username_form.is_valid():
            profile_username_form.save()

        return redirect("members:member_profile", pk=user.pk)

    else:
        user_form = UserTypeEditForm(instance=user, prefix="user_type_input")
        profile_username_form = ProfileUsernameEditForm(
            instance=user.profile, prefix="username_input"
        )

    return render(
        request,
        "members/member_profile.html",
        {
            "user_form": user_form,
            "profile_username_form": profile_username_form,
            "user": user,
            # "profile": Profile,
        },
    )
