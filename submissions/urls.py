from django.urls import path

from . import views

app_name = "submissions"

urlpatterns = [
    path("event/", views.EventSubmissionView.as_view(), name="event"),
    path("project/", views.ProjectSubmissionView.as_view(), name="project"),
    path("thanks/", views.ThanksView.as_view(), name="thanks"),
]
