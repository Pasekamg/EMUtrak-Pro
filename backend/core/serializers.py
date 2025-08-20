from rest_framework import serializers
from .models import Patient, Audit

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id','name','diagnosis','discipline','doctor','admitted','admission_date','day','sticker','remarks','created_at','updated_at']

class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = ['id','at','actor','role','action','details']
