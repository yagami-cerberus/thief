from tempfile import NamedTemporaryFile
from django.core.files import File
from django.db import models
from os import path
import urlparse
import urllib2

from thief.auction.models import YahooProductNo, RutenProductNo, RakutenProductNo

class Product(models.Model):
    title = models.CharField('\xe5\xbb\xa0\xe7\x89\x8c', max_length=1024, null=False)
    
    model_id = models.CharField('\xe5\x9e\x8b\xe8\x99\x9f', max_length=255, null=True)
    group = models.CharField('\xe5\x88\x86\xe9\xa1\x9e', max_length=255, null=True)
    
    jan = models.CharField('JAN\xe6\xa2\x9d\xe7\xa2\xbc', max_length=255, null=True)
    release_date = models.CharField('\xe7\x99\xbc\xe5\x94\xae\xe6\x97\xa5', max_length=255, null=True, blank=True)
    weight = models.CharField('\xe9\x87\x8d\xe9\x87\x8f', max_length=255, null=True, blank=True)
    size = models.CharField('\xe5\xb0\xba\xe5\xaf\xb8 (\xe5\xaf\xacx\xe6\xb7\xb1x\xe9\xab\x98)', max_length=255, null=True, blank=True)
    
    keywords = models.CharField('\xe9\x97\x9c\xe9\x8d\xb5\xe5\xad\x97', max_length=255, null=True, blank=True)
    
    summary = models.TextField('\xe7\xb0\xa1\xe4\xbb\x8b', null=True, blank=True)
    price = models.IntegerField('\xe5\x83\xb9\xe6\xa0\xbc', null=True, blank=True)
    color = models.CharField('\xe9\xa1\x8f\xe8\x89\xb2', max_length=255, null=True, blank=True)
    details = models.TextField('\xe7\x94\xa2\xe5\x93\x81\xe8\xaa\xaa\xe6\x98\x8e', null=True, blank=True)
    
    yahoo_no = models.ForeignKey(YahooProductNo, null=True, blank=True)
    ruten_no = models.ForeignKey(RutenProductNo, null=True, blank=True)
    rakuten_no = models.ForeignKey(RakutenProductNo, null=True, blank=True)
    
    # TODO: This method is broken and going to be removed.
    @classmethod
    def import_from(cls, data):
        p = Product(vendor=data.get('vendor', 'unknow'), item_id='',
            title=data.get('title') or 'No title', url='', source_price=data.get('target_price'),
            summary=data.get('summary'), color=data.get('color'), details=data.get('details'))
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
            'keywords': self.keywords,
            'summary': self.summary,
            'start_price': self.price,
            'target_price': self.price,
            'color': self.color,
            'details': self.details
        }
        
        if self.yahoo_no_id:
            data['yahoo_no'], data['yahoo_catalog_name'] = self.yahoo_no.title
        if self.ruten_no_id:
            data['ruten_no'], data['ruten_catalog_name'] = self.ruten_no.title
        if self.rakuten_no_id:
            data['rakuten_no'], data['rakuten_catalog_name'] = self.rakuten_no.title

        attach_counter = 1
        attach_name = self.jan or ("_%s" % self.pk)
        attach_files = []
        for img in self.productimage_set.order_by("pk"):
            if not path.isfile(img.image.path): continue
            ext = path.splitext(img.image.path)[-1]
            arcname = "%s_%02d%s" % (attach_name, attach_counter, ext)
            attach_files.append((img.image.path, arcname))
            data['image_%s' % attach_counter] = arcname

            attach_counter += 1

        return data, attach_files
    
    def __str__(self):
        return "%i#%s" % (self.pk, self.title)

class ProductReference(models.Model):
    product = models.ForeignKey(Product, null=False)
    
    vendor = models.CharField(max_length=255, null=False)
    url = models.URLField(max_length=1024, null=True)
    
    price = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    jan = models.CharField('JAN\xe6\xa2\x9d\xe7\xa2\xbc', max_length=255, null=True, blank=True)
    release_date = models.CharField('\xe7\x99\xbc\xe5\x94\xae\xe6\x97\xa5', max_length=255, null=True, blank=True)
    weight = models.CharField('\xe9\x87\x8d\xe9\x87\x8f', max_length=255, null=True, blank=True)
    size = models.CharField('\xe5\xb0\xba\xe5\xaf\xb8', max_length=255, null=True, blank=True)
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, null=False)
    image = models.ImageField(upload_to=path.join('data', 'images'), null=False)
