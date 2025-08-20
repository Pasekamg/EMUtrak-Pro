from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Patient, Audit
from .serializers import PatientSerializer, AuditSerializer
from .permissions import IsEditorOrReadOnly, IsAdmin

def audit(actor, role, action, details=None):
    Audit.objects.create(actor=actor, role=role, action=action, details=details or {})

class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # default role 'admin' for superusers, else 'editor' for staff, else 'viewer'
        role = 'admin' if user.is_superuser else ('editor' if user.is_staff else 'viewer')
        token['role'] = role
        return token

class MyTokenView(TokenObtainPairView):
    serializer_class = MyTokenSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-updated_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated & IsEditorOrReadOnly]

    def perform_create(self, serializer):
        role = self.request.headers.get('X-Role','viewer')
        actor = self.request.user.username or 'user'
        instance = serializer.save(created_by=self.request.user)
        audit(actor, role, 'CAPTURE', {'id': instance.id, 'name': instance.name})

    def perform_update(self, serializer):
        role = self.request.headers.get('X-Role','viewer')
        actor = self.request.user.username or 'user'
        instance = serializer.save()
        audit(actor, role, 'UPDATE', {'id': instance.id})

    def perform_destroy(self, instance):
        role = self.request.headers.get('X-Role','viewer')
        actor = self.request.user.username or 'user'
        audit(actor, role, 'DELETE_ROW', {'id': instance.id, 'name': instance.name})
        instance.delete()

class AuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Audit.objects.all().order_by('-at')
    serializer_class = AuditSerializer
    permission_classes = [IsAuthenticated & IsAdmin]
