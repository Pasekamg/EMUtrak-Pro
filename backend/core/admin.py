from django.contrib import admin
from .models import Patient, Audit
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id','name','diagnosis','discipline','doctor','admission_date','day','updated_at')
    search_fields = ('name','diagnosis','doctor','sticker')
@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('id','at','actor','role','action')
    search_fields = ('actor','action')
