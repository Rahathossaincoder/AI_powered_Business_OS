from django.db import models


class Organization(models.Model):
    organization_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150, unique=True)
    business_type = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    timezone = models.CharField(max_length=64, default='UTC')
    logo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Branch(models.Model):
    branch_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='branches')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_main_branch = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'code'], name='unique_branch_code_per_organization')
        ]
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class OrganizationSetting(models.Model):
    setting_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='settings')
    key = models.CharField(max_length=100)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization_settings'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'key'], name='unique_setting_key_per_organization')
        ]
        ordering = ['key']

    def __str__(self):
        return f'{self.organization.name}: {self.key}'
