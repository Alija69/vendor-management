from django.urls import path
from .views import *
urlpatterns = [
    path('/vendors', VendorListAPIView.as_view(), name='vendor-list'),
    path('/vendors/<int:pk>', VendorDetailAPIView.as_view(), name='vendor-detail'),
    path('/purchase_orders', PurchaseOrderListCreateAPIView.as_view(), name='purchase-order-list-create'),
    path('/purchase_orders/<int:pk>', PurchaseOrderDetailAPIView.as_view(), name='purchase-order-detail'),
    path('/vendors/<int:vendor_id>/performance', VendorPerformanceAPIView.as_view(), name='vendor-performance'),
    path('/purchase_orders/<int:po_id>/acknowledge', PurchaseOrderAcknowledgmentAPIView.as_view(), name='purchase-order-acknowledge'),
]
