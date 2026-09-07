from django.urls import path

from .views import LoginView, LogoutView, RefrescarView, YoView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refrescar/", RefrescarView.as_view(), name="refrescar"),
    path("yo/", YoView.as_view(), name="yo"),
]
