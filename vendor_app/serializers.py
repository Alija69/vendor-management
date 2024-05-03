from rest_framework import serializers
from .models import Vendor,PurchaseOrder,HistoricalPerformance
from datetime import datetime

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ('created_at', 'updated_at')


class PurchaseOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrder
        exclude = ('created_at', 'updated_at')
        
class PurchaseOrderAcknowledgmentSerializer(serializers.ModelSerializer):
    acknowledgment_date = serializers.DateTimeField(required=True)

    class Meta:
        model = PurchaseOrder
        fields = ['acknowledgment_date']
        
class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name','on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']
        
class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        exclude = ('created_at', 'updated_at')