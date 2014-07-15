from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.files import File
import mimetypes
import urlparse
import urllib2
import json

from thief.products.models import Product, ProductMeta, ProductImage
from thief.products import forms
from thief.vendors.models import Cache
from thief.vendors import get_vendor, ProductOverview, GoogleImageSearch
from thief.rest import ThiefREST, ThiefRestAPI

class products(ThiefREST):
    template = 'products.html'
    
    def get(self, request):
        return {'products': Product.objects.order_by('title').all()}
    
class search_product(ThiefREST):
    def get(self, request):
        return render(request, 'search_product.html')

class query_vendor(ThiefRestAPI):
    def get(self, request):
        vendor_cls = get_vendor(request.GET.get('vendor_name'))
        vendor = vendor_cls()
        is_cache, results = vendor.search(request.GET.get('keyword'))
    
        return {'status': True, 'is_cache': is_cache,
            'results': [r.to_dict() for r in results]}

class create_product(ThiefREST):
    template = 'create_product.html'
    
    def find_cached_product(self, vendor_name, keyword, item_id):
        for item in Cache.get_cache(vendor_name, 'search', keyword):
            if item['item_id'] == item_id:
                return ProductOverview.from_dict(item)
            else:
                return None
    
    def get(self, request):
        v_product = self.find_cached_product(
            request.GET['vendor'], request.GET['keyword'],
            request.GET['item_id']
        )
        
        product = Product(vendor=v_product.vendor, item_id=v_product.item_id,
            title=v_product.title, url=v_product.url, price=v_product.price,
            currency=v_product.currency, ean=v_product.ean,
            release_date=v_product.release_date, weight=v_product.weight,
            size=v_product.size)
        product.save()
        
        return redirect(reverse('product', args=(product.id, )))
        
class product(ThiefREST):
    template = 'product.html'
    
    def get(self, request, id):
        product = Product.objects.get(id=id)
        return {'p': product}
    
    def post(self, request):
        form = forms.Product(request.POST)
        product = form.save()
        return redirect(reverse('product', args=(product.id, )))
        
    def delete(self, request, id):
        print(id)
    
class edit_meta(ThiefREST):
    template = 'products/edit_meta.html'
    
    def get(self, request, id):
        product = Product.objects.get(id=id)
        try:
            meta = product.productmeta
            form = forms.ProductMeta(instance=meta)
        except ProductMeta.DoesNotExist:
            form = forms.ProductMeta()
            
        return {'p': product, 'form': form}
    
    def post(self, request, id):
        product = Product.objects.get(id=id)
        try:
            meta = product.productmeta
        except ProductMeta.DoesNotExist:
            meta = ProductMeta(product=product)

        form = forms.ProductMeta(request.POST, instance=meta)

        if form.is_valid():
            form.save()
            return redirect(reverse('product', args=(product.id, )))
        else:
            return {'p': product, 'form': form}
            
        
class edit_image(ThiefREST):
    template = 'products/edit_images.html'
    
    def download_image(self, product, url):
        if not (url.startswith('http://') or url.startswith('https://')):
            return
            
        request = urllib2.urlopen(url)
        filename = request.headers.get('Content-Disposition')
        
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(request.read())
        img_temp.flush()
        
        if not filename:
            filename = urlparse.urlsplit(url)[2].split("/")[-1]
        
        pi = ProductImage(product=product)
        pi.image.save(filename, File(img_temp))
        pi.save()
        
    def get(self, request, id):
        product = Product.objects.get(id=id)
        gis = GoogleImageSearch()
        is_cache, gis_images = gis.search(product.title)
        
        return {'p': product, 'gis': gis_images}
    
    def post(self, request, id):
        product = Product.objects.get(id=id)
        
        image_urls = request.POST.getlist('images')
        image_uploaded = request.FILES.getlist('files')
        
        image_delete = request.POST.getlist('delete')
        
        for url in image_urls:
            self.download_image(product, url)
        
        for file in image_uploaded:
            pi = ProductImage(product=product)
            pi.image.save(file.name, file)
            pi.save()
        
        for img in product.productimage_set.filter(id__in=image_delete):
            img.image.delete()
            img.delete()
        
        return redirect(reverse('product', args=(product.id, )))
        
class product_image(ThiefREST):
    def get(self, request, id):
        img = ProductImage.objects.get(id=id)
        mimetype, padding = mimetypes.guess_type(img.image.name)
        return HttpResponse(img.image.file, mimetype=mimetype)
    