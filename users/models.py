from django.db import models

class User(models.Model):
    nickname    = models.CharField(max_length=20, null=True)
    kakao_id    = models.BigIntegerField()
    kakao_email = models.CharField(max_length=50)

    class Meta:
        db_table = 'users'

class Address(models.Model):
    user    = models.ForeignKey('user', on_delete=models.CASCADE)
    address = models.CharField(max_length=100)

    class Meta:
        db_table = 'addresses'

class Bookmark(models.Model):
    posting = models.ForeignKey('postings.posting', on_delete=models.CASCADE)
    user    = models.ForeignKey('user', on_delete=models.CASCADE)

    class Meta:
        db_table = 'bookmarks'

class Follow(models.Model):
    follower = models.ForeignKey('user', on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey('user', on_delete=models.CASCADE, related_name='followed')

    class Meta:
        db_table = 'follows'

class Cart(models.Model):
    user           = models.ForeignKey('user', on_delete=models.CASCADE)
    product_option = models.ForeignKey('products.productoption', on_delete=models.CASCADE)
    count          = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'carts'

class PurchaseHistory(models.Model):
    user                 = models.ForeignKey('user', on_delete=models.DO_NOTHING)
    purchased_product    = models.ForeignKey('products.productoption', on_delete=models.DO_NOTHING)
    purchased_quantity   = models.IntegerField()
    purchased_price      = models.IntegerField()
    purchased_time       = models.DateTimeField(auto_now_add=True)
    paypal_payer_id      = models.CharField(max_length=50)
    paypal_payment_id    = models.CharField(max_length=100)
    paypal_payment_token = models.CharField(max_length=200)

    class Meta:
        db_table = 'purchase_histories'
