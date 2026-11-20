from django.conf import settings
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.templatetags.static import static


def version(request):
    """Commit of the running build, e.g. to compare the live site with main."""
    commit = settings.APP_COMMIT
    response = JsonResponse({"commit": commit, "short": commit[:7]})
    response["Cache-Control"] = "no-store"
    return response


def favicon(request):
    """Browsers ask for /favicon.ico regardless of the <link> tags.

    Resolved per request: the hashed static URL needs the manifest, which
    only exists after collectstatic.
    """
    return HttpResponsePermanentRedirect(static("core/img/favicon.ico"))
