from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClientViewSet,
    ProductViewSet,
    LicenseTypeViewSet,
    PricingViewSet,
    OrderViewSet,
    OrderItemViewSet,
    LicenseViewSet,
    LicenseActivationViewSet,
    SupportTicketViewSet,
)


router = DefaultRouter()
router.register(r"clients", ClientViewSet)
router.register(r"products", ProductViewSet)
router.register(r"license-types", LicenseTypeViewSet)
router.register(r"pricing", PricingViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"order-items", OrderItemViewSet)
router.register(r"licenses", LicenseViewSet)
router.register(r"license-activations", LicenseActivationViewSet)
router.register(r"support-tickets", SupportTicketViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

