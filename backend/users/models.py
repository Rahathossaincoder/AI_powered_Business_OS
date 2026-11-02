from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "users"


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "employees"