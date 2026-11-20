from django.test import TestCase

from projects.models import Project, ProjectKind


class ProjectTests(TestCase):
    def test_public_shows_only_published_projects(self):
        common = {
            "kind": ProjectKind.SHOP,
            "city": "[City]",
            "country": "[Country]",
            "link": "https://example.org/",
            "short_description": "x",
        }
        live = Project.objects.create(name="[Live]", **common)
        Project.objects.create(name="[Draft]", live=False, **common)
        self.assertQuerySetEqual(Project.objects.public(), [live])
