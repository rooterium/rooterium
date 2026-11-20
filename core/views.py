from django.conf import settings
from django.http import JsonResponse


def version(request):
    """Commit of the running build, e.g. to compare the live site with main."""
    commit = settings.APP_COMMIT
    response = JsonResponse({"commit": commit, "short": commit[:7]})
    response["Cache-Control"] = "no-store"
    return response
