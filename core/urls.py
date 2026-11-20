from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("version", views.version, name="version"),
    # Browsers ask for /favicon.ico regardless of the <link> tags.
    path("favicon.ico", views.favicon, name="favicon"),
]
