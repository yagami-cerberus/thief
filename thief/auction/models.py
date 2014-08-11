from django.db import models

class ProductTypeNo(models.Model):
    class Meta:
        abstract = True
    
    no = models.CharField(max_length=256, null=False)
    title = models.CharField(max_length=1024, null=False)

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

class Keyword(models.Model):
    group = models.CharField(max_length=256, null=False)
    keyword = models.CharField(max_length=256, null=False)

    @classmethod
    def get_groups(cls):
        kw_groups = {item[0] for item in Keyword.objects.annotate(c=models.Count('group')).values_list('group')}
        kw_groups = kw_groups.union(
            {item[0] for item in KeywordSet.objects.annotate(c=models.Count('group')).values_list('group')}
        )
        return sorted(kw_groups)
    
class KeywordSet(models.Model):
    group = models.CharField(max_length=256, null=False)
    set = models.CharField(max_length=4096, null=False)

    @classmethod
    def get_groups(cls):
         return {item[0] for item in cls.objects.annotate(c=models.Count('group')).values_list('group')}
    