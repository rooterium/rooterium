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


def make_project(**kwargs):
    defaults = {
        "name": "[Project]",
        "kind": ProjectKind.SHOP,
        "city": "[City]",
        "country": "[Country]",
        "link": "https://example.org/",
        "short_description": "[Short description]",
    }
    return Project.objects.create(**(defaults | kwargs))


class ProjectListPageTests(TestCase):
    def setUp(self):
        make_project(name="[Carpet shop]", kind=ProjectKind.SHOP)
        make_project(name="[Duduk ensemble]", kind=ProjectKind.MUSIC)
        make_project(name="[Draft project]", live=False)

    def test_lists_published_projects(self):
        response = self.client.get("/projects/")
        self.assertContains(response, "<title>Projects – Rooterium</title>", html=True)
        self.assertContains(response, '<meta name="description" content="Shops,')
        self.assertContains(response, "[Carpet shop]")
        self.assertContains(response, "[Duduk ensemble]")
        self.assertNotContains(response, "[Draft project]")

    def test_filter_by_type(self):
        response = self.client.get("/projects/?type=music")
        self.assertContains(response, "[Duduk ensemble]")
        self.assertNotContains(response, "[Carpet shop]")
        self.assertContains(
            response, "<title>Projects: Music – Rooterium</title>", html=True
        )
        self.assertContains(
            response,
            '<a class="chip" href="?type=music" aria-current="page">Music</a>',
            html=True,
        )

    def test_unknown_type_shows_all(self):
        response = self.client.get("/projects/?type=nonsense")
        self.assertContains(response, "[Carpet shop]")
        self.assertContains(response, "[Duduk ensemble]")

    def test_pagination_keeps_the_filter(self):
        for number in range(24):
            make_project(name=f"[Music {number:02}]", kind=ProjectKind.MUSIC)
        response = self.client.get("/projects/?type=music")
        self.assertContains(response, 'href="?type=music&amp;page=2"')

    def test_main_navigation_and_home_page_link_to_projects(self):
        self.assertContains(
            self.client.get("/projects/"),
            '<a href="/projects/" aria-current="page">Projects</a>',
            html=True,
        )
        self.assertContains(self.client.get("/"), 'href="/projects/"')
