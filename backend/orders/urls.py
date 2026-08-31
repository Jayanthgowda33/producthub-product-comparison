from django.urls import path

from .views import CartItemView, CartView, CheckoutView, OrderListView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/<int:item_id>/', CartItemView.as_view(), name='cart-item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('my-orders/', OrderListView.as_view(), name='my-orders'),
]