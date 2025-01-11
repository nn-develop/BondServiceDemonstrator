from django.urls import path, include
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter
from .views import BondViewSet, PortfolioAnalysisView

router = DefaultRouter()
router.register(r"manage", BondViewSet)

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
    path("analysis/", PortfolioAnalysisView.as_view(), name="portfolio-analysis"),
]
