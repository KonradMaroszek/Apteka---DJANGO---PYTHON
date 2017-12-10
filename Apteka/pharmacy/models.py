from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    amount = models.IntegerField(default=0)
    product_logo = models.FileField()
    description = models.TextField(default="", max_length=9999)
    discount = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('pharmacy:product_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return self.name


class Basket(models.Model):
    def get_absolute_url(self):
        return reverse('pharmacy:basket', kwargs={'pk':self.pk})

class History(models.Model):
    user = models.CharField(max_length=100)
    order = models.BigIntegerField()
    price = models.FloatField()
    status = models.CharField(max_length=100)
    basket = models.TextField(max_length=9999)

    def get_absolute_url(self):
        return reverse('pharmacy:history', kwargs={'pk':self.pk})

