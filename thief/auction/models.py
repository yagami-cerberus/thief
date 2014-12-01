import itertools

from django.db import models

class ProductTypeNo(models.Model):
    class Meta:
        abstract = True
    
    catalog = models.ForeignKey('auction.Catalog', null=False, blank=False)
    manufacturer = models.CharField(u'\u5ee0\u724c', max_length=32, null=False, blank=True, default="")
    no = models.CharField(u'\u4ee3\u78bc', max_length=256, null=False)
    
    @classmethod
    def get_no(cls, catalog, manufacturer):
        m = cls.objects.filter(catalog=catalog, manufacturer=manufacturer).first()
        if m:
            return m.no
        else:
            m = cls.objects.filter(catalog=catalog, manufacturer="").first()
            if m: return m.no
            return ""
        
    def __repr__(self):
    	return "%s %s" % (self.no, self.title)

    def __str__(self):
        return self.__repr__()
    
class YahooProductNo(ProductTypeNo):
    brand = '\xe9\x9b\x85\xe8\x99\x8e\xe6\x8b\x8d\xe8\xb3\xa3'

class RutenProductNo(ProductTypeNo):
    brand = '\xe9\x9c\xb2\xe5\xa4\xa9\xe6\x8b\x8d\xe8\xb3\xa3'

class RakutenProductNo(ProductTypeNo):
    brand = '\xe6\xa8\x82\xe5\xa4\xa9'

class AuctionConfigs(models.Model):
    key = models.CharField(max_length=256, null=False)
    value = models.CharField(max_length=256, null=False)

class Catalog(models.Model):
    name = models.CharField(max_length=256, null=False)

    def __str__(self):
        return self.name.encode("utf8")

    def grouped_keywords(self):
        return {i[0]: list(i[1]) 
            for i in itertools.groupby(self.keyword_set.order_by("manufacturer"), lambda e: e.manufacturer)}

class Keyword(models.Model):
    catalog = models.ForeignKey(Catalog, null=False)
    manufacturer = models.CharField(max_length=32, null=False, blank=True, default="")
    keyword = models.CharField(max_length=256, null=False)
    
    def __repr__(self):
        return "<Keyword: %s for %s>" % (self.keyword, self.manufacturer)
    
class KeywordSet(models.Model):
    catalog = models.ForeignKey(Catalog, null=False)
    manufacturer = models.CharField(max_length=32, null=False, blank=True, default="")
    set = models.CharField(max_length=4096, null=False)

class Color(models.Model):
    name = models.CharField(max_length=128, null=False)
    symbol = models.CharField(max_length=64, null=False)
