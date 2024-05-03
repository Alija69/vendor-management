from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Vendor, PurchaseOrder
from .serializers import *
from django.db.models import Avg, ExpressionWrapper, F, DurationField
from django.http import Http404
from django.db import models

class VendorListAPIView(APIView):
    def get(self, request):
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VendorDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        vendor = self.get_object(pk)
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)

    def put(self, request, pk):
        vendor = self.get_object(pk)
        serializer = VendorSerializer(vendor, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        vendor = self.get_object(pk)
        vendor.delete()
        return Response({"msg":"deleted"},status=status.HTTP_204_NO_CONTENT)

class PurchaseOrderListCreateAPIView(APIView):
    def get(self, request):
        vendor_id = request.query_params.get('vendor')
        if vendor_id:
            purchase_orders = PurchaseOrder.objects.filter(vendor=vendor_id)
        else:
            purchase_orders = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseOrderDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        purchase_order = self.get_object(pk)
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)

    def put(self, request, pk):
        purchase_order = self.get_object(pk)
        serializer = PurchaseOrderSerializer(purchase_order, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        purchase_order = self.get_object(pk)
        purchase_order.delete()
        return Response({"msg":"deleted"},status=status.HTTP_204_NO_CONTENT)


class VendorPerformanceAPIView(APIView):
    
    def get_object(self, pk):
        try:
            return Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            raise Http404

    def get(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
            serializer = VendorPerformanceSerializer(vendor)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class PurchaseOrderAcknowledgmentAPIView(APIView):
    
    def get_object(self, po_id):
        try:
            return PurchaseOrder.objects.get(pk=po_id)
        except PurchaseOrder.DoesNotExist:
            raise Http404
        
    def update_vendor_performance(self, vendor_id):
        vendor = Vendor.objects.get(pk=vendor_id)

        completed_pos = PurchaseOrder.objects.filter(vendor=vendor_id, status='completed')
        on_time_deliveries = completed_pos.filter(delivery_date__lte=models.F('acknowledgment_date')).count()
        vendor.on_time_delivery_rate = (on_time_deliveries / completed_pos.count()) * 100 if completed_pos.count() else 0

        vendor.quality_rating_avg = completed_pos.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0

        response_times = completed_pos.exclude(acknowledgment_date=None).annotate(response_time=ExpressionWrapper(F('acknowledgment_date') - F('issue_date'),output_field=DurationField())).aggregate(Avg('response_time'))['response_time__avg']
        vendor.average_response_time = response_times.total_seconds() / (3600 * 24) if response_times else 0 #convert into days

        fulfilled_pos = completed_pos.filter(status='completed')
        vendor.fulfillment_rate = (fulfilled_pos.count() / completed_pos.count()) * 100 if completed_pos.count() else 0

        historical_performance_data = {
            'vendor': vendor.id,
            'date': datetime.now(),
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate,
        }
        
        serializer = HistoricalPerformanceSerializer(data=historical_performance_data)
        if serializer.is_valid():
            serializer.save()
        vendor.save()
   
    def post(self, request, po_id):
        try:
            purchase_order = self.get_object(po_id)
            serializer = PurchaseOrderAcknowledgmentSerializer(data=request.data)
            if serializer.is_valid():
                purchase_order.acknowledgment_date = serializer.data['acknowledgment_date']
                purchase_order.status = 'completed'
                purchase_order.save()
                self.update_vendor_performance(purchase_order.vendor_id)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PurchaseOrder.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
   