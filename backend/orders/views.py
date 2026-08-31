from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import ProductVariant
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartItemWriteSerializer, CartSerializer, OrderSerializer


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        return Response(CartSerializer(cart).data)

    def post(self, request):
        serializer = CartItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant = ProductVariant.objects.get(id=serializer.validated_data['variant_id'])
        quantity = serializer.validated_data['quantity']

        cart, _ = Cart.objects.get_or_create(customer=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, variant=variant, defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        item = CartItem.objects.filter(id=item_id, cart__customer=request.user).first()
        if not item:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        quantity = request.data.get('quantity')
        if not quantity or int(quantity) < 1:
            return Response({'detail': 'quantity must be at least 1.'}, status=400)
        item.quantity = int(quantity)
        item.save()
        return Response(CartSerializer(item.cart).data)

    def delete(self, request, item_id):
        item = CartItem.objects.filter(id=item_id, cart__customer=request.user).first()
        if not item:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        cart = item.cart
        item.delete()
        return Response(CartSerializer(cart).data)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(customer=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for item in cart.items.select_related('variant'):
                if item.variant.stock_quantity < item.quantity:
                    return Response(
                        {'detail': f'Not enough stock for {item.variant}.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            order = Order.objects.create(
                customer=request.user,
                shipping_address=request.data.get('shipping_address', ''),
                status=Order.Status.PENDING,
            )
            total = 0
            for item in cart.items.select_related('variant'):
                price = item.variant.price
                OrderItem.objects.create(
                    order=order, variant=item.variant,
                    quantity=item.quantity, price_at_purchase=price,
                )
                item.variant.stock_quantity -= item.quantity
                item.variant.save()
                total += price * item.quantity

            order.total_amount = total
            order.save()
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')