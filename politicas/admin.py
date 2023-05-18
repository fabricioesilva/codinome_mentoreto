from django.contrib import admin
from .models import (
    PolicyRules,
    PolicyAcepted,
    PolicyChanges,
    DevPolicyRules,
    DevPolicyAcepted,
    DevPolicyChanges,
    AboutUs,
    AboutUsChanges,
)
from django_summernote.admin import SummernoteModelAdmin


class PolicyRulesAdmin(SummernoteModelAdmin):
    model = PolicyRules
    summernote_fields = ('text',)
    readonly_fields = ['created_date', 'user', 'user_email', 'policy_user_id']

    def save_model(self, request, obj, form, change):
        if obj.active:
            try:
                atual = PolicyRules.objects.get(
                    language=obj.language, active=True)
                atual.active = False
                atual.save()
            except PolicyRules.DoesNotExist:
                atual = None
        obj.user = request.user
        obj.user_email = obj.user.email
        obj.policy_user_id = obj.user.pk
        super().save_model(request, obj, form, change)
        if change:
            PolicyChanges.objects.create(
                user_email=obj.user.email,
                policy_user_id=obj.user.pk,
                policy_title=obj.title,
                policy_status=str(obj.active),
                policy_content=obj.text,
                policy_pkey=obj.pk,
                action='Changed'
            )
        else:
            PolicyChanges.objects.create(
                user_email=obj.user.email,
                policy_user_id=obj.user.pk,
                policy_title=obj.title,
                policy_status=str(obj.active),
                policy_content=obj.text,
                policy_pkey=obj.pk,
                action='Created'
            )

    def delete_model(self, request, obj):
        PolicyChanges.objects.create(
            user_email=obj.user.email,
            policy_user_id=obj.user.pk,
            policy_title=obj.title,
            policy_status=str(obj.active),
            policy_content=obj.text,
            policy_pkey=obj.pk,
            action='Deleted'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            PolicyChanges.objects.create(
                user_email=obj.user.email,
                policy_user_id=obj.user.pk,
                policy_title=obj.title,
                policy_status=str(obj.active),
                policy_content=obj.text,
                policy_pkey=obj.pk,
                action='Deleted'
            )
        queryset.delete()
        # super().delete_queryset(request, queryset)


class PolicyAcceptedAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'user_email',
                       'profile_id', 'acept_date', 'policy']


class PolicyChangesAdmin(admin.ModelAdmin):
    readonly_fields = ['user_email', 'policy_user_id', 'policy_status',
                       'policy_content', 'policy_pkey', 'mod_date', 'action']


admin.site.register(PolicyRules, PolicyRulesAdmin)
admin.site.register(PolicyAcepted, PolicyAcceptedAdmin)
admin.site.register(PolicyChanges, PolicyChangesAdmin)


class DevPolicyRulesAdmin(SummernoteModelAdmin):
    model = DevPolicyRules
    summernote_fields = ('text',)
    readonly_fields = ['created_date', 'user', 'user_email', 'policy_user_id']

    def save_model(self, request, obj, form, change):
        if obj.active:
            try:
                atual = DevPolicyRules.objects.get(
                    language=obj.language, active=True)
                atual.active = False
                atual.save()
            except DevPolicyRules.DoesNotExist:
                atual = None
        obj.user = request.user
        obj.user_email = obj.user.email
        obj.policy_user_id = obj.user.pk
        super().save_model(request, obj, form, change)
        if change:
            DevPolicyChanges.objects.create(
                user_email=obj.user.email,
                policy_user_id=obj.user.pk,
                policy_title=obj.title,
                policy_status=str(obj.active),
                policy_content=obj.text,
                policy_pkey=obj.pk,
                action='Changed'
            )
        else:
            DevPolicyChanges.objects.create(
                user_email=obj.user.email,
                policy_user_id=obj.user.pk,
                policy_title=obj.title,
                policy_status=str(obj.active),
                policy_content=obj.text,
                policy_pkey=obj.pk,
                action='Created'
            )

    def delete_model(self, request, obj):
        DevPolicyChanges.objects.create(
            user_email=obj.user.email,
            policy_user_id=obj.user.pk,
            policy_title=obj.title,
            policy_status=str(obj.active),
            policy_content=obj.text,
            policy_pkey=obj.pk,
            action='Deleted'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            DevPolicyChanges.objects.create(
                user_email=obj.user.email,
                policy_user_id=obj.user.pk,
                policy_title=obj.title,
                policy_status=str(obj.active),
                policy_content=obj.text,
                policy_pkey=obj.pk,
                action='Deleted'
            )
        queryset.delete()
        # super().delete_queryset(request, queryset)


class DevPolicyAcceptedAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'user_email',
                       'profile_id', 'acept_date', 'policy']


class DevPolicyChangesAdmin(admin.ModelAdmin):
    readonly_fields = ['user_email', 'policy_user_id', 'policy_status',
                       'policy_content', 'policy_pkey', 'mod_date', 'action']


admin.site.register(DevPolicyRules, DevPolicyRulesAdmin)
admin.site.register(DevPolicyAcepted, DevPolicyAcceptedAdmin)
admin.site.register(DevPolicyChanges, DevPolicyChangesAdmin)


class AboutUsAdmin(SummernoteModelAdmin):
    model = AboutUs
    summernote_fields = ('text',)
    readonly_fields = ['created_date', 'user', 'user_email', 'staff_id']

    def save_model(self, request, obj, form, change):
        if obj.active:
            try:
                atual = AboutUs.objects.get(
                    language=obj.language, active=True)
                atual.active = False
                atual.save()
            except AboutUs.DoesNotExist:
                atual = None
        obj.user = request.user
        obj.user_email = obj.user.email
        obj.staff_id = obj.user.pk
        super().save_model(request, obj, form, change)
        if change:
            AboutUsChanges.objects.create(
                user_email=obj.user.email,
                user_id=obj.user.pk,
                title=obj.title,
                content=obj.text,
                pkey=obj.pk,
                action='Changed'
            )
        else:
            AboutUsChanges.objects.create(
                user_email=obj.user.email,
                user_id=obj.user.pk,
                title=obj.title,
                content=obj.text,
                pkey=obj.pk,
                action='Created'
            )

    def delete_model(self, request, obj):
        AboutUsChanges.objects.create(
            user_email=obj.user.email,
            user_id=obj.user.pk,
            title=obj.title,
            content=obj.text,
            pkey=obj.pk,
            action='Deleted'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            AboutUsChanges.objects.create(
                user_email=obj.user.email,
                user_id=obj.user.pk,
                title=obj.title,
                content=obj.text,
                pkey=obj.pk,
                action='Deleted with qs'
            )
        queryset.delete()


class AboutUsChangesAdmin(admin.ModelAdmin):
    readonly_fields = ['user_email', 'user_id',
                       'content', 'pkey', 'mod_date', 'action']


admin.site.register(AboutUs, AboutUsAdmin)
admin.site.register(AboutUsChanges, AboutUsChangesAdmin)
