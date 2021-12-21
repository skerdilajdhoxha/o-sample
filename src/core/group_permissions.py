import logging

from django.contrib.auth.models import Permission


USER_TYPE = [
    "ohi_user",
    "blu_user",
    "general_user",
    "ohi_admin",
    "blu_admin",
    "super_user",
]
MODELS = [
    "album",
    "Album Category",
    "album photos",
    "invoice",
    "product",
    "Product Category",
    "product photos",
]
PERMISSIONS = ["view", "add", "change", "delete"]


def get_permissions(user_type):
    """
    Used to create Groups for the first time, if they don't exist.
    Depending on the user_type given on creation of the user object, user is added to Group with given permissions.
    If the group exists then user is added to that group and this is not used at all.
    """
    permission_list = []
    if user_type == USER_TYPE[0]:
        for model in MODELS[0:3]:
            for permission in PERMISSIONS[0:1]:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
    elif user_type == USER_TYPE[1]:
        for model in MODELS[3:]:
            for permission in PERMISSIONS[0:1]:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
    elif user_type == USER_TYPE[2]:
        for model in MODELS:
            for permission in PERMISSIONS[0:1]:
                print(
                    "//////////////////////////////////////////////////////////"
                    + permission
                )
                print("-----------------------------------------" + permission)
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
    elif user_type == USER_TYPE[3]:
        for model in MODELS[0:3]:
            for permission in PERMISSIONS:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
        for model in MODELS[3:]:
            for permission in PERMISSIONS[0:1]:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
    elif user_type == USER_TYPE[4]:
        for model in MODELS[3:]:
            for permission in PERMISSIONS:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
        for model in MODELS[0:3]:
            for permission in PERMISSIONS[0:1]:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
    elif user_type == USER_TYPE[5]:
        for model in MODELS:
            for permission in PERMISSIONS:
                name = "Can {} {}".format(permission, model)
                try:
                    model_add_perm = Permission.objects.get(name=name)
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".format(name))
                    continue
                permission_list.append(model_add_perm)
    return permission_list
