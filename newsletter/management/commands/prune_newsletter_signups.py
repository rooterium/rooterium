from django.core.management.base import BaseCommand

from newsletter.models import UNCONFIRMED_DAYS, NewsletterSubscriber


class Command(BaseCommand):
    help = (
        f"Delete newsletter sign-ups not confirmed within {UNCONFIRMED_DAYS} "
        "days. Every new sign-up does this too; run it from cron so it also "
        "happens when nobody signs up."
    )

    def handle(self, *args, **options):
        deleted, _ = NewsletterSubscriber.objects.stale().delete()
        self.stdout.write(f"Deleted {deleted} unconfirmed sign-up(s).")
