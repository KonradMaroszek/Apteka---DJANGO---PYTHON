from django.db import models
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    amount = models.IntegerField(default=0)
    product_logo = models.CharField(default = 'null', max_length=300)
    description = models.TextField(default = "", max_length=9999)

    def __str__(self):
        return self.name