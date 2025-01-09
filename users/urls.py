from django.urls import path
from django.urls.resolvers import URLPattern
from .views import RegisterView, CustomObtainAuthToken, CustomLogoutView

urlpatterns: list[URLPattern] = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", CustomObtainAuthToken.as_view(), name="user-login"),
    path("logout/", CustomLogoutView.as_view(), name="user-logout"),
]
