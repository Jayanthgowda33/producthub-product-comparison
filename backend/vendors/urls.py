from rest_framework.routers import DefaultRouter

from .views import VendorProductViewSet

router = DefaultRouter()
router.register('my-products', VendorProductViewSet, basename='vendor-product')

urlpatterns = router.urls