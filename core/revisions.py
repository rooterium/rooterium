"""Changing page fields from code without touching the editor's drafts.

A page with unpublished changes has a newer draft in its latest revision;
the database row still holds the live version. Code that fills in fields
must start from the latest version (or it would drop the draft's changes)
and must not publish it (or it would publish the editor's draft).
"""

from wagtail.models import Page


def latest_version(page):
    """The page as the editor sees it in the admin: the draft if any."""
    page = page.specific
    if page.has_unpublished_changes:
        return page.get_latest_revision_as_object()
    return page


def save_version(page):
    """Save `page` (from `latest_version`) as a new revision. Publish it
    only if the page is live and had no unpublished draft."""
    had_draft = Page.objects.filter(pk=page.pk, has_unpublished_changes=True).exists()
    was_live = Page.objects.filter(pk=page.pk, live=True).exists()
    revision = page.save_revision()
    if was_live and not had_draft:
        revision.publish()
    return revision
