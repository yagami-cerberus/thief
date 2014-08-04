from tempfile import NamedTemporaryFile
import mimetypes
import logging
import zipfile
import os

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, StreamingHttpResponse
from django.core.files import File
from django.contrib import messages
from datetime import datetime

from thief.products.models import Product, ProductImage
from thief.products import forms
from thief.auction.csv_packer import CsvPacker, CsvUnpacker
from thief.auction.models import Keyword
from thief.vendors.rakuten import Rakuten
from thief.vendors.models import Cache
from thief.vendors import ProductOverview, GoogleImageSearch
from thief.rest import ThiefREST

logger = logging.getLogger(__name__)
SESSION_LAST_UPLOAD_TIME_KEY = 'lutk'
SESSION_LAST_UPLOAD_PRODUCTS_KEY = 'lupk'

class products(ThiefREST):
    template = 'products/products.html'
    
    # List
    def get(self, request):
        return {'products': Product.objects.order_by('title').all()}
    
    # Create
    def post(self, request):
        v_product = ProductOverview.from_dict({key: request.POST[key] for key in request.POST})
        product = Product(vendor=v_product.vendor, item_id=v_product.item_id,
            title=v_product.title, url=v_product.url, source_price=v_product.price,
            source_currency=v_product.currency, jan=v_product.jan,
            release_date=v_product.release_date, weight=v_product.weight,
            size=v_product.size)
        product.save()
        
        # self.try_fetch_image(product)
        return redirect(reverse('prepare_product', args=(product.id, )))
        # return redirect(reverse('product', args=(product.id, )))
    
    # Delete
    def delete(self, request):
        for p in Product.objects.filter(pk__in=request.POST.getlist('p')):
            logger.info("Delete product: %s" % p)
            unlink_files = [i.image.name for i in p.productimage_set.all()]
            p.delete()
            for fname in unlink_files:
                try:
                    os.unlink(fname)
                except OSError:
                    pass
            
        return redirect(reverse('products'))
    
    # Special hook
    def try_fetch_jan(self, productOverview):
        if productOverview.url.startswith("http://product.rakuten.co.jp/"):
            productOverview.jan = Rakuten().fetch_jan(productOverview.url)
        
    # Special hook
    def try_fetch_image(self, product):
        gis = GoogleImageSearch()
        is_cache, gis_images = gis.search(product.title)
        if len(gis_images) > 0:
            product.fetch_image_from_url(gis_images[0].url)
        
class product(ThiefREST):
    template = 'products/product.html'
    
    def get(self, request, id):
        product = Product.objects.get(id=id)
        return {'p': product}

class prepare_product(product):
    template = 'products/prepare_product.html'
    
    def post(self, request, id):
        product = Product.objects.get(id=id)
        action = request.POST.get("job")
        
        if action == "google-img":
            return self.google_img(product)
        elif action == "jan":
            return self.jan(product)
        else:
            return HttpResponse("false", content_type="application/json")
        
    def google_img(self, product):
        gis = GoogleImageSearch()
        is_cache, gis_images = gis.search(product.title)
        if len(gis_images) > 0:
            product.fetch_image_from_url(gis_images[0].url)
            return HttpResponse("true", content_type="application/json")
        else:
            return HttpResponse("false", content_type="application/json")

    def jan(self, product):
        if product.url.startswith("http://product.rakuten.co.jp/"):
            jan = Rakuten().fetch_jan(product.url)
            if jan:
                product.jan = jan
                product.save()
                return HttpResponse("true", content_type="application/json")
            else:
                return HttpResponse("false", content_type="application/json")
    
class edit_product(ThiefREST):
    template = 'products/edit.html'
    
    def get(self, request, id):
        product = Product.objects.get(id=id)
        form = forms.Product(instance=product)
        keywords = Keyword.objects.all().values_list('keyword', flat=True)
        
        return {'form': form, 'keywords': keywords}
        
    def post(self, request, id):
        product = Product.objects.get(id=id)
        form = forms.Product(request.POST, instance=product)
        
        if form.is_valid():
            form.save()
            return redirect(reverse('product', args=(product.id, )))
        else:
            return {'p': product, 'form': form}
        
class edit_image(ThiefREST):
    template = 'products/edit_images.html'
            
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
            self.fetch_image_from_url(url)
        
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
        return StreamingHttpResponse(img.image.file, mimetype=mimetype)

class download_csv(ThiefREST):
    def get(self, request, auction_type):
        try:
            wrapper = CsvPacker(auction_type)
            wrapper.pack(Product.objects.filter(pk__in=request.GET.getlist('p')))

            response = StreamingHttpResponse(wrapper.get_fileobject(), mimetype="application/zip")
            response['Content-Disposition'] = 'attachment; filename="%s.zip"' % auction_type
            return response

        except RuntimeError as e:
            return HttpResponse(e.args[0], content_type="text/plain")

class upload_csv(ThiefREST):
    template = 'products/upload_csv.html'
    
    def get(self, request):
        lu = request.session.get(SESSION_LAST_UPLOAD_TIME_KEY)
        lp = request.session.get(SESSION_LAST_UPLOAD_PRODUCTS_KEY)
        
        products = lp and Product.objects.filter(pk__in=lp.split(',')) or []
        
        return {
            'upload_success': request.session.pop("upload_success", None),
            'last_upload': lu,
            'last_upload_products': products
        }
        
    def post(self, request):
        auction_type = request.POST.get('auction_type')
        csv_file = request.FILES.get('csv_file')
        unpacker = CsvUnpacker(auction_type, csv_file)
        
        idset = []
        for data in unpacker.load():
            data['vender'] = auction_type
            p = Product.import_from(data)
            idset.append("%s"%p.id)
        
        request.session["upload_success"] = True
        request.session[SESSION_LAST_UPLOAD_TIME_KEY] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request.session[SESSION_LAST_UPLOAD_PRODUCTS_KEY] = ','.join(idset)
        
        return redirect(reverse('upload_products_csv'))
        