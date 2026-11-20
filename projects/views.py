from urllib.parse import urlencode

from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from core.seo import SeoMixin

from .models import Project, ProjectKind


class ProjectListView(SeoMixin, ListView):
    """Published projects by name, optionally filtered by type (`?type=`)."""

    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 24
    page_title = _("Projects")
    meta_description = _(
        "Shops, start-ups, music and crafts initiatives that carry Armenian "
        "traditions into today."
    )

    def get_kind(self) -> str:
        """The selected type, or "" for all (unknown values count as all)."""
        kind = self.request.GET.get("type", "")
        return kind if kind in ProjectKind.values else ""

    def get_queryset(self):
        projects = Project.objects.public().select_related("logo")
        if kind := self.get_kind():
            projects = projects.filter(kind=kind)
        return projects

    def get_page_title(self) -> str:
        if kind := self.get_kind():
            return f"{_('Projects')}: {ProjectKind(kind).label}"
        return super().get_page_title()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kinds"] = ProjectKind.choices
        context["current_kind"] = self.get_kind()
        if context["current_kind"]:
            context["pagination_query"] = urlencode({"type": context["current_kind"]})
        return context
