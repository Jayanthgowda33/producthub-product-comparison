from rest_framework import viewsets

from config.permissions import IsVendor
from products.models import Product
from products.serializers import ProductDetailSerializer, VendorProductWriteSerializer


class VendorProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsVendor]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user.vendor_profile)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ProductDetailSerializer
        return VendorProductWriteSerializer

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)