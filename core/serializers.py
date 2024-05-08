from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Studio, StudioImage, Reservation


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["id"] = self.user.id
        data["email"] = self.user.email
        data["is_superuser"] = self.user.is_superuser
        data["user_type"] = self.user.user_type
        data["name"] = self.user.name
        data["phone"] = self.user.phone
        data["role"] = self.user.user_type
        return data
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_type', 'email', 'name', 'phone', 'create_date']
        read_only_fields = ['id', 'create_date']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'user_type', 'name', 'phone']
        extra_kwargs = {'password': {'write_only': True}}
        
class StudioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudioImage
        fields = ['id', 'studio', 'image']
        read_only_fields = ['id']

class StudioSerializer(serializers.ModelSerializer):
    images = StudioImageSerializer(many=True, read_only=True)
    class Meta:
        model = Studio
        fields = ['id', 'owner', 'name', 'address', 'created_at', 'price', 'rate' , 'images']
        read_only_fields = ['id', 'created_at']
        

class StudioCreateSerializer(serializers.ModelSerializer):
    images = StudioImageSerializer(many=True, read_only=True)
    class Meta:
        model = Studio
        fields = ['owner', 'name', 'address', 'price', 'rate']
        

        

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'customer', 'studio', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['customer', 'studio', 'start_date', 'end_date']

    def validate(self, data):
        """
        Validate the reservation start and end dates.
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Check if start date is before end date
        if start_date >= end_date:
            raise serializers.ValidationError("Start date must be before end date.")

        # Check if the studio is available during the specified time period
        studio = data.get('studio')
        conflicting_reservations = Reservation.objects.filter(studio=studio, start_date__lte=end_date, end_date__gte=start_date)
        if conflicting_reservations.exists():
            raise serializers.ValidationError("Studio is not available during this time.")

        return data
