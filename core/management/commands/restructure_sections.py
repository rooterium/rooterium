"""Bring the page tree to the six temple sections (ADR 0018).

Run once after the migrations of the temple redesign (milestone T2), on
every database that has content from version 1; safe to run again. See
`core/sections.py` for what it does. No `--allow-production` flag: this is
a structural step for production as well, like a migration.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.sections import ensure_sections


class Command(BaseCommand):
    help = "Migrate theme pages to the six sections and create the Symbols categories."

    def handle(self, *args, **options):
        with transaction.atomic():
            ensure_sections(log=self.stdout.write)
        self.stdout.write(self.style.SUCCESS("Sections ready."))
