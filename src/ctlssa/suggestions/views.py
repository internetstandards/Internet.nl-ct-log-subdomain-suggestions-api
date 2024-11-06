from django.http import JsonResponse

from .logic.suggest import suggest_subdomains


def suggest(request):
    return JsonResponse(
        suggest_subdomains(
            request.GET.get("domain", None),
            request.GET.get("suffix", "nl"),
            request.GET.get("period_in_days", 365),
            request.GET.get("max_date", None),
        ),
        safe=False,
    )
