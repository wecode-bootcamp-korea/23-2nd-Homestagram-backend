from django.db import models

class Product(models.Model):
    product_name  = models.CharField(max_length=20)
    price         = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail_url = models.URLField(max_length=1000)

    class Meta:
        db_table = 'products'

class Color(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'colors'

class ProductImage(models.Model):
    product   = models.ForeignKey('product', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=1000)

    class Meta:
        db_table = 'product_images'

class ProductOption(models.Model):
    product = models.ForeignKey('product', on_delete=models.CASCADE)
    color   = models.ForeignKey('color', on_delete=models.SET_DEFAULT, default=1)
    stock   = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_options'