from datetime import date, timedelta
import datetime
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin



class UserManager(BaseUserManager):
    """
    class manager for providing a User(AbstractBaseUser) full control
    on this objects to create all types of User and this roles.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        pass data  to '_create_user' for creating normal_user .
        """
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        pass data to '_create_user' for creating super_user .
        """
        if email is None:
            raise TypeError("Users must have an email address.")
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("user_type", User.admin)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    admin , studio_owner, customer = (
        'Admin',
        'Studio_owner',
        'Customer'
    )
    USER_TYPES = (
        (admin, admin),
        (studio_owner, studio_owner),
        (customer, customer),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email = models.EmailField(db_index=True, unique=True, null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=17, unique=True, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email or ''} - {self.phone or ''}"


class Studio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField()
    rate = models.IntegerField(default=1, choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    def get_available_days(self):
        reservations = self.reservation_set.all()
        reserved_days = set()
        for reservation in reservations:
            start_date = reservation.start_date
            end_date = reservation.end_date
            delta = timedelta(days=1)
            while start_date <= end_date:
                reserved_days.add(start_date)
                start_date += delta
        available_days = []
        today = date.today()
        while today.year == self.created_at.year: 
            if today not in reserved_days:
                available_days.append(today)
            today += delta
        return available_days

    def __str__(self):
        return self.name


class StudioImage(models.Model):
    studio = models.ForeignKey(Studio, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='studio_images')

    def __str__(self):
        return f"Image for {self.studio.name}"
    


class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reservation for {self.studio.name} by {self.customer.email}"

    def can_cancel(self):
        """
        Check if the reservation can be canceled.
        Customers can cancel reservations within 15 minutes of booking.
        """
        current_time = datetime.now()
        booking_time = self.created_at
        elapsed_time = current_time - booking_time
        return elapsed_time <= timedelta(minutes=15)
    