from django.urls import path

from . import views

app_name = "newsletter"

urlpatterns = [
    path("", views.SignupView.as_view(), name="signup"),
    path("check-your-inbox/", views.CheckInboxView.as_view(), name="check_inbox"),
    path("confirm/<str:token>/", views.ConfirmView.as_view(), name="confirm"),
    path(
        "unsubscribe/<str:token>/",
        views.UnsubscribeView.as_view(),
        name="unsubscribe",
    ),
]
