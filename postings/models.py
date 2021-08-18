from django.db import models

class Posting(models.Model):
    content     = models.TextField(max_length=500, null=True)
    user        = models.ForeignKey('users.user', on_delete=models.SET_NULL, null=True)
    image_url   = models.URLField(max_length=1000)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    design_type = models.ForeignKey('designtype', on_delete=models.SET_DEFAULT, default=1)

    class Meta:
        db_table = 'postings'

class Tag(models.Model):
    posting    = models.ForeignKey('posting', on_delete=models.CASCADE)
    product    = models.ForeignKey('products.product', on_delete=models.CASCADE)
    coordinate = models.CharField(max_length=25)

    class Meta:
        db_table = 'tags'

class Comment(models.Model):
    posting    = models.ForeignKey('posting', on_delete=models.CASCADE)
    user       = models.ForeignKey('users.user', on_delete=models.SET_NULL, null=True)
    content    = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'

class DesignType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'design_types'