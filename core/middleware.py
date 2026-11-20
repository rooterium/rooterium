"""Content-Security-Policy for public pages (ADR 0013).

Django 5.2 has no built-in CSP (Django 6.0 has; switch when moving to the
next LTS). The admin areas are excluded: Wagtail's admin needs inline
scripts and styles, and its page preview frames the public templates.
"""

from django.conf import settings

EXCLUDED_PREFIXES = ("/admin/", "/django-admin/")


class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.policy = "; ".join(
            f"{directive} {' '.join(sources)}"
            for directive, sources in settings.CONTENT_SECURITY_POLICY.items()
        )

    def __call__(self, request):
        response = self.get_response(request)
        if (
            self.policy
            and not request.path.startswith(EXCLUDED_PREFIXES)
            # The 500 page is deliberately standalone with inline styles.
            and response.status_code < 500
            and "Content-Security-Policy" not in response
        ):
            response["Content-Security-Policy"] = self.policy
        return response
