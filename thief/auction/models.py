from django.db import models

class ProductTypeNo(models.Model):
    class Meta:
        abstract = True
    
    no = models.CharField(max_length=256, null=False)
    title = models.CharField(max_length=1024, null=False)

class YahooProductNo(ProductTypeNo):
    brand = '\xe9\x9b\x85\xe8\x99\x8e\xe6\x8b\x8d\xe8\xb3\xa3'

class RutenProductNo(ProductTypeNo):
    brand = '\xe9\x9c\xb2\xe5\xa4\xa9\xe6\x8b\x8d\xe8\xb3\xa3'
