from django.urls import path

from .views import AssistantView, SearchView, SimilarProductsView

urlpatterns = [
    path('search/', SearchView.as_view(), name='ai-search'),
    path('similar/<int:product_id>/', SimilarProductsView.as_view(), name='ai-similar'),
    path('assistant/', AssistantView.as_view(), name='ai-assistant'),
]