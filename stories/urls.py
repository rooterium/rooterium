from django.urls import path

from . import views

app_name = "stories"

urlpatterns = [
    path("", views.StoryListView.as_view(), name="list"),
]
