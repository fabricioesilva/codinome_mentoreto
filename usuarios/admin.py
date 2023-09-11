from django.contrib import admin
from .models import CustomUser, UserEmailCheck, Preferences, DeletedUser, EnderecoCobranca


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserEmailCheck)
admin.site.register(Preferences)
admin.site.register(DeletedUser)
admin.site.register(EnderecoCobranca)
