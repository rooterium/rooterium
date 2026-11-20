from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.models import DraftStateMixin, RevisionMixin


class ProjectKind(models.TextChoices):
    SHOP = "shop", _("Shop")
    STARTUP = "startup", _("Start-up")
    INITIATIVE = "initiative", _("Initiative")
    MUSIC = "music", _("Music")
    CRAFTS = "crafts", _("Crafts")
    OTHER = "other", _("Other")


class ProjectQuerySet(models.QuerySet):
    def public(self):
        return self.filter(live=True)


class Project(DraftStateMixin, RevisionMixin, models.Model):
    """A shop, start-up or initiative (snippet with draft/publish)."""

    name = models.CharField(_("name"), max_length=200)
    kind = models.CharField(_("type"), max_length=20, choices=ProjectKind.choices)
    city = models.CharField(_("city"), max_length=100)
    country = models.CharField(_("country"), max_length=100)
    link = models.URLField(_("link"))
    logo = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        verbose_name=_("logo"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    short_description = models.TextField(
        _("short description"), max_length=300, help_text=_("One or two sentences.")
    )
    submitted_by_email = models.EmailField(
        _("submitted by (email)"),
        blank=True,
        help_text=_("Only for contacting the submitter. Never shown publicly."),
    )

    objects = ProjectQuerySet.as_manager()

    panels = [
        FieldPanel("name"),
        FieldPanel("kind"),
        FieldRowPanel([FieldPanel("city"), FieldPanel("country")]),
        FieldPanel("link"),
        FieldPanel("logo"),
        FieldPanel("short_description"),
        FieldPanel("submitted_by_email"),
    ]

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["name"]

    def __str__(self):
        return self.name
