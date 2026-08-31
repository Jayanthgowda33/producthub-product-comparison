from rest_framework import serializers

from products.models import ProductVariant
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='variant.product.title', read_only=True)
    unit_price = serializers.DecimalField(source='variant.price', max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'variant', 'product_title', 'quantity', 'unit_price', 'line_total')

    def get_line_total(self, obj):
        return obj.variant.price * obj.quantity


class CartItemWriteSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_variant_id(self, value):
        if not ProductVariant.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product variant not found.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total')

    def get_total(self, obj):
        return sum(item.variant.price * item.quantity for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='variant.product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'variant', 'product_title', 'quantity', 'price_at_purchase')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'total_amount', 'shipping_address', 'items', 'created_at')
        read_only_fields = ('status', 'total_amount')