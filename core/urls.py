from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    ReservationAPIView,
    StudioAPIView,
    UserAPIView,
)

urlpatterns = [
    path("auth/jwt/create/", CustomTokenObtainPairView.as_view(), name="token_create"),
    path('users/', UserAPIView.as_view(), name='users'),
    path('studios/', StudioAPIView.as_view(), name='studios'),
    path('reservations/', ReservationAPIView.as_view(), name='reservations'),

]
