from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, AuditViewSet, MyTokenView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'audit', AuditViewSet, basename='audit')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', MyTokenView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
