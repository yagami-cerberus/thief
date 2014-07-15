from django.db import models
from os import path

from thief.auction.models import YahooProductNo, RutenProductNo

class Product(models.Model):
    vendor = models.CharField(max_length=255, null=False)
    item_id = models.CharField(max_length=255, null=False)
    title = models.CharField(max_length=1024, null=False)
    
    url = models.URLField(null=True)
    price = models.CharField(max_length=255, null=True)
    currency = models.CharField(max_length=255, null=True)

    ean = models.CharField(max_length=255, null=True)
    release_date = models.CharField(max_length=255, null=True)
    weight = models.CharField(max_length=255, null=True)
    size = models.CharField(max_length=255, null=True)
    
class ProductMeta(models.Model):
    product = models.OneToOneField(Product, primary_key=True)
    
    # YAHOO
    yahoo_no = models.ForeignKey(YahooProductNo, null=True)
    #        RUTEN
    ruten_no = models.ForeignKey(RutenProductNo, null=True)
    # YAHOO, RUTEN
    goods_location = models.CharField('\xe7\x89\xa9\xe5\x93\x81\xe6\x89\x80\xe5\x9c\xa8\xe5\x9c\xb0', max_length=255, null=True)
    # YAHOO, RUTEN
    auction_duration = models.IntegerField('\xe6\x8b\x8d\xe8\xb3\xa3\xe6\x9c\x9f\xe9\x96\x93', null=True)
    # YAHOO, RUTEN
    auction_end_at = models.IntegerField('\xe7\xb5\x90\xe6\x9d\x9f\xe6\x99\x82\xe9\x96\x93', null=True)
    # YAHOO, RUTEN
    auto_expend = models.IntegerField('\xe8\x87\xaa\xe5\x8b\x95\xe5\xbb\xb6\xe9\x95\xb7', null=True)
    # YAHOO, RUTEN
    # end_advance = models.BooleanField('\xe6\x8f\x90\xe5\x89\x8d\xe7\xb5\x90\xe6\x9d\x9f', null=True)
    # YAHOO, RUTEN
    usage_status = models.CharField('\xe7\x89\xa9\xe5\x93\x81\xe6\x96\xb0\xe8\x88\x8a', max_length=255, null=True)
    
    keywords = models.CharField('\xe9\x97\x9c\xe9\x8d\xb5\xe5\xad\x97', max_length=255, null=True)
    
    summary = models.TextField('\xe7\xb0\xa1\xe4\xbb\x8b', null=True)
    price = models.IntegerField('\xe5\x83\xb9\xe6\xa0\xbc', null=True)
    amount = models.IntegerField('\xe6\x95\xb8\xe9\x87\x8f', null=True) 
    color = models.CharField('\xe9\xa1\x8f\xe8\x89\xb2', max_length=255, null=True)
    details = models.TextField('\xe7\x94\xa2\xe5\x93\x81\xe8\xaa\xaa\xe6\x98\x8e', null=True)
    # spec = models.TextField('\xe7\x94\xa2\xe5\x93\x81\xe8\xa6\x8f\xe6\xa0\xbc', null=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, null=False)
    image = models.ImageField(upload_to=path.join('data', 'images'), null=False)
