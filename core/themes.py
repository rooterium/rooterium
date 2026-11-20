"""The fixed list of themes (ADR 0014).

Stories get their theme from their theme index page; places have it as a
field. "Events" and "Projects" are map filters, not themes.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.TextChoices):
    HISTORY = "history", _("History")
    TRADITIONS = "traditions", _("Traditions")
    MYTHS = "myths", _("Myths")
    SYMBOLS = "symbols", _("Symbols")
    MUSIC = "music", _("Music")
