from django.urls import path

from products.views import ProductDetailView

urlpatterns = [
    path('/<int:product_id>/detail', ProductDetailView.as_view())
]