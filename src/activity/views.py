from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from .models import Action


@permission_required("activity.can_view_action", raise_exception=True)
def activity_logs(request):
    all_actions = Action.objects.all()
    page = request.GET.get("page", 1)

    paginator = Paginator(all_actions, 20)
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        actions = paginator.page(1)
    except EmptyPage:
        actions = paginator.page(paginator.num_pages)

    index = actions.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = paginator.page_range[start_index:end_index]

    return render(
        request,
        "activity/activity_log.html",
        {"actions": actions, "page_range": page_range},
    )
