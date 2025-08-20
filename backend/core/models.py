from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    name = models.CharField(max_length=120)
    diagnosis = models.CharField(max_length=200)
    discipline = models.CharField(max_length=120)
    doctor = models.CharField(max_length=120, blank=True, default='')
    admitted = models.CharField(max_length=8, default='Yes')
    admission_date = models.DateField(null=True, blank=True)
    day = models.IntegerField(default=0)
    sticker = models.CharField(max_length=120, blank=True, default='')
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='patients_created')

    def __str__(self):
        return self.name

class Audit(models.Model):
    at = models.DateTimeField(auto_now_add=True)
    actor = models.CharField(max_length=64)
    role = models.CharField(max_length=24)
    action = models.CharField(max_length=64)
    details = models.JSONField(default=dict)
