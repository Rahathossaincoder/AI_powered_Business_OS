from django.db import models


class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = "inventory"