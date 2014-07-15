from django.db import models
from datetime import datetime, timedelta
import json

EXPIRE = timedelta(days=7)

class Cache(models.Model):
    vendor = models.CharField(max_length=255, null=False)
    method = models.CharField(max_length=255, null=False)
    keyword = models.CharField(max_length=1024, null=False)
    create_at = models.DateTimeField(null=False)
    data = models.TextField(null=False)
    
    @classmethod
    def get_cache(cls, vendor, method, keyword):
        cache = cls.objects.filter(vendor=vendor, method=method, keyword=keyword).first()
        if cache:
            if cache.create_at.replace(tzinfo=None) + EXPIRE > datetime.now():
                return json.loads(cache.data)
            else:
                cache.delete()
                return None
        else:
            return None
    
    @classmethod
    def set_cache(cls, vendor, method, keyword, data):
        for cache in cls.objects.filter(vendor=vendor, method=method, keyword=keyword):
            cache.delete()
        
        cache = cls(vendor=vendor, method=method, keyword=keyword, create_at=datetime.now(),
                    data=json.dumps(data))
        cache.save()
        return cache
    