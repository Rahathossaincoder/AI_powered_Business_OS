from django.contrib import admin

from .models import Branch, Organization, OrganizationSetting


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'name', 'slug', 'business_type', 'is_active')
    search_fields = ('name', 'slug', 'email')
    list_filter = ('is_active', 'business_type')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_id', 'organization', 'code', 'name', 'is_main_branch', 'is_active')
    search_fields = ('code', 'name', 'email')
    list_filter = ('organization', 'is_main_branch', 'is_active')


@admin.register(OrganizationSetting)
class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_id', 'organization', 'key')
    search_fields = ('key', 'organization__name')
    list_filter = ('organization',)
