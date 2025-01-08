from django.contrib import admin
from django.urls import path, include
from django.urls.resolvers import URLResolver
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# URL configuration for the project
urlpatterns: list[URLResolver] = [
    # Path for Django Admin Panel (for managing the application via UI)
    path("admin/", admin.site.urls),
    # Include URLs for the 'users' application, which handles user-related views like registration, login, etc.
    path("api/users/", include("users.urls")),
    # Include URLs for the 'bonds' application, which manages bond-related operations (like creating bonds, updating bonds, etc.)
    path("api/bonds/", include("bonds.urls")),
    # Endpoint for generating the OpenAPI schema for the project
    # The schema defines the structure of the API, which is used for generating documentation and for interacting with the API
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Interactive Swagger UI for exploring and testing the API through a user-friendly interface
    # The 'url_name' parameter connects the Swagger UI to the OpenAPI schema generated at the 'schema/' endpoint
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
]
