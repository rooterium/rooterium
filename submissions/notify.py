"""Email to the editor about a new submission."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from wagtail.admin.admin_url_finder import AdminURLFinder

logger = logging.getLogger(__name__)


def summary(obj, field_names) -> list[tuple[str, str]]:
    """(label, value) pairs of the submitted fields, for the email."""
    rows = []
    for name in field_names:
        field = obj._meta.get_field(name)
        if field.choices:
            value = getattr(obj, f"get_{name}_display")()
        else:
            value = getattr(obj, name)
        rows.append((str(field.verbose_name), "" if value is None else str(value)))
    return rows


def notify_editor(request, obj, field_names) -> None:
    """Tell the editor that `obj` (a draft event or project) waits for review.

    Never fails the submission: the draft is already saved and shows up in
    the admin anyway. Without `EDITOR_NOTIFICATION_EMAIL` nothing is sent.
    """
    recipient = settings.EDITOR_NOTIFICATION_EMAIL
    if not recipient:
        logger.warning("EDITOR_NOTIFICATION_EMAIL is not set; no email sent.")
        return
    edit_url = AdminURLFinder().get_edit_url(obj)
    context = {
        "object": obj,
        "kind": obj._meta.verbose_name,
        "summary": summary(obj, field_names),
        "edit_url": request.build_absolute_uri(edit_url) if edit_url else "",
    }
    subject = _("New %(kind)s suggested: %(name)s") % {
        "kind": obj._meta.verbose_name,
        "name": str(obj),
    }
    body = render_to_string("submissions/email/notification.txt", context)
    try:
        send_mail(subject, body, None, [recipient])
    except Exception:
        logger.exception("Could not send the submission notification.")
