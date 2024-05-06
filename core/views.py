from django.db import transaction
from django.db.models.query_utils import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    ReservationCreateSerializer,
    ReservationSerializer,
    StudioCreateSerializer,
    StudioImageSerializer,
    StudioSerializer,
    UserSerializer,
)
from .models import Reservation, Studio, User


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(Q(email=request.data["email"]) | Q(phone=request.data["email"]))
        if not user.exists():
            raise InvalidToken(("user does not exist"))
        user = user.first()

        request.data["email"] = user.email

        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(
            {
                "user": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )
    

class UserAPIView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            user_id = request.user.id
            instance = User.objects.get(pk=user_id)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            user_id = request.user.id
            instance = User.objects.get(pk=user_id)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)



# Studio's Views

class StudioAPIView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Studio.objects.all()
    permission_classes = [permissions.IsAuthenticated]


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StudioSerializer
        return StudioCreateSerializer

    def get_queryset(self):
        if self.request.get('owner_profile') is True:
            return Studio.objects.filter(owner=self.request.user)
        return Studio.objects.all()

    def get(self, request, *args, **kwargs):
        studio_id = request.data.get('id')
        if studio_id:
            studio = get_object_or_404(Studio, pk=studio_id)
            serializer = self.get_serializer(studio)
            return Response(serializer.data)
        else:
            studios = self.get_queryset()
            serializer = self.get_serializer(studios, many=True)
            return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            if request.user.user_type == 'Studio_owner':
                studio_serializer = self.get_serializer(data=request.data)
                image_serializer = StudioImageSerializer(data=request.data.get('images'), many=True)
                if studio_serializer.is_valid() and image_serializer.is_valid():
                    studio_instance = studio_serializer.save(owner=request.user)
                    image_serializer.save(studio=studio_instance)
                    return Response(studio_serializer.data, status=status.HTTP_201_CREATED)
                return Response({"studio_errors": studio_serializer.errors, "image_errors": image_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You are not authorized to create a studio."}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            studio_id = request.data.get('id')
            instance = Studio.objects.filter(pk=studio_id, owner=request.user).first()
            if instance:
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You are not authorized to update this studio or the studio does not exist."}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            studio_id = request.data.get('id')
            instance = Studio.objects.filter(pk=studio_id, owner=request.user).first()
            if instance:
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "You are not authorized to delete this studio or the studio does not exist."}, status=status.HTTP_403_FORBIDDEN)
        

# Reservations 

class ReservationAPIView(generics.ListCreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Reservation.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET' :
            return ReservationSerializer
        return ReservationCreateSerializer

    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return Reservation.objects.all()
        return Reservation.objects.filter(Q(owner=self.request.user) | Q(customer=self.request.user))

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            reservation_id = request.data.get('id')
            instance = Reservation.objects.filter(pk=reservation_id, owner=request.user).first()
            if instance:
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You are not authorized to update this reservation or the reservation does not exist."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            reservation_id = request.data.get('id')
            instance = Reservation.objects.filter(pk=reservation_id, customer=request.user).first()
            if instance:
                if instance.can_cancel():
                    instance.delete()
                    return Response({"detail": "Reservation cancelled successfully."}, status=status.HTTP_200_OK)
                return Response({"detail": "Cancellation window has expired. You cannot cancel this reservation."}, status=status.HTTP_400_BAD_REQUEST)
            raise Response({"detail":"Reservation does not exist or you are not authorized to cancel it."}, status=status.HTTP_403_FORBIDDEN )