
from itertools import ifilter
import socket
import csv

from django.core.urlresolvers import reverse
from django.utils.timezone import now, timedelta

from thief.rest import ThiefREST, ThiefRestAPI
from thief.vendors import ProductOverview, GoogleImageSearch
from thief.vendors import get_vendor
from thief.auction.models import KeywordSet, Catalog
from thief.products.models import Product, ProductReference
from thief.products.forms import ProductReference as ProductReferenceForm

current_local_time_str = lambda: (now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

class search_product(ThiefREST):
	template = 'search_product.html'

	def get(self, request):
		return {}

class query(ThiefRestAPI):
    def get(self, request):
        vendor_cls = get_vendor(request.GET.get('vendor_name'))
        vendor = vendor_cls()
        is_cache, results = vendor.search(request.GET.get('keyword'))
    
        return {'status': True, 'is_cache': is_cache,
            'results': [r.to_dict() for r in results[:10]]}

class create(object):
    def post(self, request):
        pass
    
class batch_import(ThiefREST):
    template = 'vendors/batch_import.html'
    
    def find_clumn_index(self, header):
        manufacturer_index, model_index, group_index, price_index = 0, 1, 2, 3
        for i in xrange(len(header)):
            name = header[i]
            if name.decode("big5", "ignore") == u'\u5ee0\u724c':
                manufacturer_index = i
            elif name.decode("big5", "ignore") == u'\u578b\u865f':
                model_index = i
            elif name.decode("big5", "ignore") == u'\u54c1\u9805':
                group_index = i
            elif name.decode("big5", "ignore") == u'\u50f9\u683c':
                price_index = i

        return manufacturer_index, model_index, group_index, price_index
    
    def get(self, request):
		return {}
        
    def post(self, request):
        f = request.FILES.get('csv_file')
        reader = csv.reader(f)
        ma_i, mo_i, g_i, pr_i = self.find_clumn_index(reader.next())
        data = [{'t': r[mo_i].decode("big5", "ignore"), 'g': r[g_i].decode("big5", "ignore"),
                    'm': r[ma_i].decode("big5", "ignore"),'p': r[pr_i].decode("big5", "ignore")}
                    for r in ifilter(lambda i: i[mo_i], reader)]
                    
        return {'data': data}

class import_item(ThiefRestAPI):
    class Shallow:
        def __getattr__(self, key):
            return ""
    
    _shallow_result = Shallow()
    
    def write_ref(self, product, vender_profile):
        ref = ProductReference(product=product)
        ref_f = ProductReferenceForm(vender_profile.to_dict(), instance=ref)
        if ref_f.is_valid(): ref_f.save()
        
    def fetch_image(self, product):
        gis = GoogleImageSearch()
        is_cache, gis_images = gis.search("%s %s" % (product.model_id, product.manufacturer))
        
        for gis_image in gis_images:
            if not (gis_image.url.startswith("http://") or gis_image.url.startswith("https://")):
                continue
            if gis_image.width < 320 or gis_image.height < 240:
                continue
            
            product.fetch_image_from_url(gis_image.url)
            return True
        return False
    
    def guess_keywords(self, catalog_id, manufacturer):
        g = KeywordSet.objects.filter(catalog_id=catalog_id, manufacturer=manufacturer).first()
        if g:
            return g.set

    def post(self, request):
        manufacturer = request.POST.get('manufacturer')
        model_id = request.POST.get('model_id')
        catalog = Catalog.objects.filter(name=request.POST.get('catalog', '')).first()
        price = request.POST.get('price')
        
        if not catalog:
            return {'st': False, 'message': 'BAD_CATALOG'}
        if not model_id:
            return {'st': False, 'message': 'BAD_MODEL_ID'}
        
        exist_item = Product.objects.filter(model_id=model_id).first()
        if exist_item:
            return {'st': False, 'url': reverse('product', args=(exist_item.id, )), 'message': 'ITEM_ALREADY_EXIST'}
        
        rakuten = self._shallow_result
        amazon = self._shallow_result
        jan = ""
        
        try:
            rakuten_vendor = get_vendor('rakuten')()
            rakuten = rakuten_vendor.search(model_id)[-1][0]
        except IndexError:
            pass
        
        try:
            jan = rakuten_vendor.fetch_jan(rakuten.url)
        except (socket.error, RuntimeError):
            pass
    
        try:
            amazon_vendor = get_vendor('amazon_jp')()
            amazon = amazon_vendor.search(model_id)[-1][0]
        except RuntimeError:
            return {'st': False, 'message': 'AMAZON_FLOW_CONTROL'}
        except IndexError:
            pass
        
        product = Product(manufacturer=manufacturer,
            model_id=model_id, catalog_id=catalog.id, release_date=amazon.release_date or rakuten.release_date,
            weight=amazon.weight, size=amazon.size, price=price, summary="", details="",
            jan=jan, created_at=current_local_time_str())
        
        product.keywords = self.guess_keywords(catalog.id, manufacturer)
        product.save()

        if not isinstance(rakuten, self.Shallow): self.write_ref(product, rakuten)
        if not isinstance(amazon, self.Shallow): self.write_ref(product, amazon)
        self.fetch_image(product)
        
        return {'st': True, 'url': reverse('product', args=(product.id, ))}
