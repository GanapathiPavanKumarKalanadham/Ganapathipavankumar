from django.contrib import admin
from .models import UserProfile
from .forms import UserProfileForm 

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm
    list_display = ('name', 'email', 'mobile_number', 'created_at')
    search_fields = ('name', 'email', 'mobile_number')
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"

    def add_view(self, request, form_url='', extra_context=None):
        # Use the default behavior for add_view
        return super().add_view(request, form_url, extra_context)

admin.site.register(UserProfile, UserProfileAdmin)