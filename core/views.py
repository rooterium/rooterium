from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView

from .seo import SeoMixin


class HomeView(SeoMixin, TemplateView):
    template_name = "core/home.html"
    # No page title: the home page uses the plain site title.


def version(request):
    """Commit of the running build, e.g. to compare the live site with main."""
    commit = settings.APP_COMMIT
    response = JsonResponse({"commit": commit, "short": commit[:7]})
    response["Cache-Control"] = "no-store"
    return response
