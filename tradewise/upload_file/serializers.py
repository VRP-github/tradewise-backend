from rest_framework import serializers
from .models import TransactionSummary

class TransactionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionSummary
        fields = '__all__'