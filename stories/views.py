from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from core.seo import SeoMixin

from .models import StoryPage, theme_pages


class StoryListView(SeoMixin, ListView):
    """All live stories, newest first. Per theme: the theme pages."""

    template_name = "stories/story_list.html"
    context_object_name = "stories"
    paginate_by = 12
    page_title = _("Stories")
    meta_description = _(
        "Stories about Armenian history, traditions, myths, symbols and music."
    )

    def get_queryset(self):
        return (
            StoryPage.objects.live()
            .select_related("hero_image")
            .order_by("-date", "-pk")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["theme_pages"] = theme_pages()
        return context
