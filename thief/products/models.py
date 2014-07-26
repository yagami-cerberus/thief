from tempfile import NamedTemporaryFile
from django.core.files import File
from django.db import models
from os import path
import urlparse
import urllib2

from thief.auction.models import YahooProductNo, RutenProductNo

class Product(models.Model):
    vendor = models.CharField(max_length=255, null=False)
    item_id = models.CharField(max_length=255, null=False)
    url = models.URLField(null=True)
    source_price = models.CharField(max_length=255, null=True)
    source_currency = models.CharField(max_length=255, null=True)
    
    title = models.CharField('\xe5\x93\x81\xe5\x90\x8d', max_length=1024, null=False)
    
    jan = models.CharField('JAN\xe6\xa2\x9d\xe7\xa2\xbc', max_length=255, null=True)
    release_date = models.CharField('\xe7\x99\xbc\xe5\x94\xae\xe6\x97\xa5', max_length=255, null=True)
    weight = models.CharField('\xe9\x87\x8d\xe9\x87\x8f', max_length=255, null=True)
    size = models.CharField('\xe5\xb0\xba\xe5\xaf\xb8', max_length=255, null=True)
    
    # YAHOO
    yahoo_no = models.ForeignKey(YahooProductNo, null=True, blank=True)
    #        RUTEN
    ruten_no = models.ForeignKey(RutenProductNo, null=True, blank=True)
    
    keywords = models.CharField('\xe9\x97\x9c\xe9\x8d\xb5\xe5\xad\x97', max_length=255, null=True, blank=True)
    
    summary = models.TextField('\xe7\xb0\xa1\xe4\xbb\x8b', null=True, blank=True)
    price = models.IntegerField('\xe5\x83\xb9\xe6\xa0\xbc', null=True, blank=True)
    amount = models.IntegerField('\xe6\x95\xb8\xe9\x87\x8f', null=True, blank=True) 
    color = models.CharField('\xe9\xa1\x8f\xe8\x89\xb2', max_length=255, null=True, blank=True)
    details = models.TextField('\xe7\x94\xa2\xe5\x93\x81\xe8\xaa\xaa\xe6\x98\x8e', null=True, blank=True)
    
    usage_status = models.CharField('\xe7\x89\xa9\xe5\x93\x81\xe6\x96\xb0\xe8\x88\x8a', max_length=255, null=True, blank=True)
    
    @classmethod
    def import_from(cls, data):
        p = Product(vendor=data.get('vendor', 'unknow'), item_id='',
            title=data.get('title') or 'No title', url='', source_price=data.get('target_price'),
            usage_status=data.get('usage_status'), summary=data.get('summary'), amount=data.get('amount'),
            color=data.get('color'), details=data.get('details'))
        p.save()
        return p
        
    def fetch_image_from_url(self, url):
        if not (url.startswith('http://') or url.startswith('https://')):
            return
        
        request = urllib2.Request(url, headers={
            "Referer": "https://www.google.com.tw/search", 
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"})
            
        response = urllib2.urlopen(request)
        filename = response.headers.get('Content-Disposition')
        
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.read())
        img_temp.flush()
        
        if not filename:
            filename = urlparse.urlsplit(url)[2].split("/")[-1]
        
        pi = ProductImage(product=self)
        pi.image.save(filename, File(img_temp))
        pi.save()
        
        return pi
        
    def export(self):
        data = {
            'title': self.title,
            'yahoo_no': self.yahoo_no_id and self.yahoo_no.no,
            'ruten_no': self.ruten_no_id and self.ruten_no.no,
            'usage_status': self.usage_status,
            'keywords': self.keywords,
            'summary': self.summary,
            'start_price': self.price,
            'target_price': self.price,
            'amount': self.amount,
            'color': self.color,
            'details': self.details
        }

        attach_counter = 1
        attach_name = self.jan or ("_%s" % self.pk)
        attach_files = []
        for img in self.productimage_set.order_by("pk"):
            if not path.isfile(img.image.path): continue
            ext = path.splitext(img.image.path)[-1]
            arcname = "%s-%s%s" % (attach_name, attach_counter, ext)
            attach_files.append((img.image.path, arcname))
            data['image_%s' % attach_counter] = arcname

            attach_counter += 1

        return data, attach_files
    
    def __str__(self):
        return "%i#%s" % (self.pk, self.title)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, null=False)
    image = models.ImageField(upload_to=path.join('data', 'images'), null=False)
