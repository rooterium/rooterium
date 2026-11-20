"""Spam protection for the public submission forms, without third parties.

Three checks (brief, section 2.7):

- Honeypot: a field people never see (hidden by CSS); bots fill it in.
- Minimum fill time: the form carries a signed timestamp; a submission
  sooner than `MIN_FILL_SECONDS` after the form was shown is refused, as is
  a missing, forged or stale timestamp.
- Rate limit: at most `RATE_LIMIT` submissions per client IP and hour,
  counted in Django's cache. The cache is per process (LocMemCache), so
  with several Gunicorn workers the effective limit is a few times higher
  – enough against floods. The IP is only hashed into the cache key, never
  stored.
"""

import hashlib
import time

from django.core import signing
from django.core.cache import cache

MIN_FILL_SECONDS = 3
MAX_FORM_AGE_SECONDS = 24 * 60 * 60
RATE_LIMIT = 5
RATE_WINDOW_SECONDS = 60 * 60

_SALT = "submissions.started"


def make_started_token() -> str:
    """Signed timestamp of the moment the form was shown."""
    return signing.dumps(time.time(), salt=_SALT)


def filled_in_too_fast(token: str) -> bool:
    """True if the token is missing, forged, too old or too young."""
    try:
        started = signing.loads(token, salt=_SALT, max_age=MAX_FORM_AGE_SECONDS)
    except signing.BadSignature, TypeError:
        return True
    try:
        age = time.time() - float(started)
    except TypeError, ValueError:
        return True
    return not MIN_FILL_SECONDS <= age <= MAX_FORM_AGE_SECONDS


def client_ip(request) -> str:
    """The client's IP. Behind Caddy, the last X-Forwarded-For entry is the
    address Caddy saw (it does not trust incoming X-Forwarded-For)."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")


def _rate_key(request) -> str:
    digest = hashlib.sha256(client_ip(request).encode()).hexdigest()[:32]
    return f"submissions:rate:{digest}"


def rate_limited(request) -> bool:
    """True if this client has used up its submissions for the hour."""
    return cache.get(_rate_key(request), 0) >= RATE_LIMIT


def count_submission(request) -> None:
    key = _rate_key(request)
    if not cache.add(key, 1, RATE_WINDOW_SECONDS):
        try:
            cache.incr(key)
        except ValueError:  # expired in between
            cache.add(key, 1, RATE_WINDOW_SECONDS)
