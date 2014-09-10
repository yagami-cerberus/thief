from tempfile import NamedTemporaryFile
import mimetypes
import logging
import zipfile
import json
import os

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.timezone import now, timedelta
from django.core.files import File
from django.contrib import messages
from datetime import datetime

from thief.products.models import Product, ProductReference, ProductImage
from thief.products import forms
from thief.auction.csv_packer import CsvPacker, CsvUnpacker
from thief.auction.models import Keyword, KeywordSet
from thief.vendors.rakuten import Rakuten
from thief.vendors.models import Cache
from thief.vendors import ProductOverview, GoogleImageSearch
from thief.rest import ThiefREST

logger = logging.getLogger(__name__)
SESSION_LAST_UPLOAD_TIME_KEY = 'lutk'
SESSION_LAST_UPLOAD_PRODUCTS_KEY = 'lupk'

current_local_time_str = lambda: (now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

class products(ThiefREST):
    template = 'products/products.html'
    order_list = ['manufacturer', 'model_id', 'release_date', 'price', 'created_at']
    
    # List
    def get(self, request):
        q = request.GET.get("q")
        o = request.GET.get("o", "0")
        
        query = Product.objects.all()
        if q:
            query = (query.filter(manufacturer__contains=q) |
                     query.filter(group__contains = q) |
                     query.filter(release_date = q) |
                     query.filter(group__contains = q))
        
        try:
            order_index = int(o)
            
            if o.startswith("-"):
                query = query.order_by("-%s" % self.order_list[order_index])
            else:
                query = query.order_by(self.order_list[order_index])
                
        except (ValueError, IndexError):
            query = query.order('manufacturer')
            o = "0"
        
        return {'products': query, 'q': request.GET.get("q"), 'g': request.GET.get("g"),
            'o': o, 'order_reference': self.order_list}
    
    # Create
    def post(self, request):
        v_product = ProductOverview.from_dict({key: request.POST[key] for key in request.POST})
        product = Product(manufacturer=v_product.manufacturer, jan=v_product.jan, release_date=v_product.release_date,
            weight=v_product.weight, size=v_product.size,
            created_at=current_local_time_str())
        
        if product.model_id:
            product.model_id = product.model_id.upper()
        
        keyword = request.POST.get('keyword')
        if keyword: product.model_id = keyword
        
        product.save()
        
        if 'vendor' in request.POST:
            ref = ProductReference(product=product)
            ref_f = forms.ProductReference(request.POST, instance=ref)
            ref_f.save()
        
        return redirect(reverse('prepare_product', args=(product.id, )))
    
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
        is_cache, gis_images = gis.search(' '.join([product.manufacturer, product.model_id]))
        if len(gis_images) > 0:
            product.fetch_image_from_url(gis_images[0].url)
            return HttpResponse("true", content_type="application/json")
        else:
            return HttpResponse("false", content_type="application/json")

    def jan(self, product):
        for r in product.productreference_set.all():
            if r.url.startswith("http://product.rakuten.co.jp/"):
                jan = Rakuten().fetch_jan(r.url)
                if jan:
                    product.jan = jan
                    product.save()
                    return HttpResponse("true", content_type="application/json")
                else:
                    return HttpResponse("false", content_type="application/json")
    
class edit_product(ThiefREST):
    template = 'products/edit.html'
    
    def get_keywords_data(self):
        return json.dumps({
            'keywords': [(k.group, k.keyword) for k in Keyword.objects.order_by("keyword").all()],
            'keyword_sets': [(k.group, k.set) for k in KeywordSet.objects.order_by("set").all()]
        })
    
    def update_keyword_set(self, product):
        if product.keywords.strip() and product.group.strip():
            KeywordSet.objects.get_or_create(set=product.keywords, group=product.group)
    
    def get(self, request, id):
        product = Product.objects.get(id=id)
        form = forms.Product(instance=product)
        keywords = Keyword.objects.all().values_list('keyword', flat=True)
        
        return {'form': form, 'kw': self.get_keywords_data()}
        
    def post(self, request, id):
        product = Product.objects.get(id=id)
        form = forms.Product(request.POST, instance=product)
        
        if form.is_valid():
            form.save()
            self.update_keyword_set(product)
            return redirect(reverse('product', args=(product.id, )))
        else:
            return {'form': form, 'kw': self.get_keywords_data()}
        
class edit_image(ThiefREST):
    template = 'products/edit_images.html'
            
    def get(self, request, id):
        product = Product.objects.get(id=id)
        gis = GoogleImageSearch()
        is_cache, gis_images = gis.search(' '.join([product.manufacturer, product.model_id]))
        
        return {'p': product, 'gis': gis_images}
    
    def post(self, request, id):
        product = Product.objects.get(id=id)
        
        image_urls = request.POST.getlist('images')
        image_uploaded = request.FILES.getlist('files')
        
        image_delete = request.POST.getlist('delete')
        
        for url in image_urls:
            product.fetch_image_from_url(url)
        
        for file in image_uploaded:
            pi = ProductImage(product=product)
            pi.image.save(file.name, file)
            pi.save()
        
        for img in product.productimage_set.filter(id__in=image_delete):
            img.image.delete()
            img.delete()
        
        # return redirect(reverse('product', args=(product.id, )))
        return redirect(reverse('edit_product_images', args=(product.id, )))
        
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

# TODO: This will not be use anymore
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
            p.created_at = current_local_time_str()
            idset.append("%s"%p.id)
        
        request.session["upload_success"] = True
        request.session[SESSION_LAST_UPLOAD_TIME_KEY] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request.session[SESSION_LAST_UPLOAD_PRODUCTS_KEY] = ','.join(idset)
        
        return redirect(reverse('upload_products_csv'))
        