from django.db import models


class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        db_table = "organizations"