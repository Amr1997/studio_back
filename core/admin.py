from django.contrib import admin
from .models import User, Studio, StudioImage, Reservation

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'user_type', 'name', 'phone', 'create_date']
    search_fields = ['email', 'name', 'phone']
    list_filter = ['user_type']

admin.site.register(User, UserAdmin)

class StudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'name', 'address', 'created_at', 'price', 'rate']
    search_fields = ['name', 'owner__email']
    list_filter = ['created_at', 'rate']

admin.site.register(Studio, StudioAdmin)

class StudioImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'studio', 'image']
    search_fields = ['studio__name']
    raw_id_fields = ['studio']

admin.site.register(StudioImage, StudioImageAdmin)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'studio', 'start_date', 'end_date', 'created_at']
    search_fields = ['customer__email', 'studio__name']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

admin.site.register(Reservation, ReservationAdmin)
