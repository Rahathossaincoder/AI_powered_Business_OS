from django.db import models


class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        db_table = "organizations"


class Branch(models.Model):
    """Stand-in for the team's Branch model (table `branches`, columns as in db.sqlite3)."""

    branch_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="branches")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True, default="")
    email = models.EmailField(null=True, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True, default="")
    address_line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    is_main_branch = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "branches"
        constraints = [
            models.UniqueConstraint(fields=["organization", "code"], name="unique_branch_code_per_organization")
        ]

    def __str__(self):
        return f"{self.code} {self.name}"