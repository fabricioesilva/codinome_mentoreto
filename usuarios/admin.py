from django.contrib import admin
from .models import CustomUser, UserEmailCheck, Preferences, DeletedUser, PerfilCobranca


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'email_checked')

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserEmailCheck)
admin.site.register(Preferences)
admin.site.register(DeletedUser)
admin.site.register(PerfilCobranca)
