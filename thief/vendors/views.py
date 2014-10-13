
from itertools import ifilter
import csv

from django.core.urlresolvers import reverse
from django.utils.timezone import now, timedelta

from thief.rest import ThiefREST, ThiefRestAPI
from thief.vendors import ProductOverview, GoogleImageSearch
from thief.vendors import get_vendor
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
        mi, gi = 0, 1
        for i in xrange(len(header)):
            name = header[i]
            if name.decode("big5", "ignore") == u'\u578b\u865f':
                mi = i
            if name.decode("big5", "ignore") == u'\u54c1\u9805':
                gi = i
            if name.decode("big5", "ignore") == u'\u50f9\u683c':
                pi = i

        return mi, gi, pi
    
    def get(self, request):
		return {}
        
    def post(self, request):
        f = request.FILES.get('csv_file')
        reader = csv.reader(f)
        mi, gi, pi = self.find_clumn_index(reader.next())
        data = [{'t': r[mi].decode("big5", "ignore"), 'g': r[gi].decode("big5", "ignore"), 'p': r[pi].decode("big5", "ignore")}
                    for r in ifilter(lambda i: i[mi], reader)]
                    
        return {'data': data}

class import_item(ThiefRestAPI):
    def write_ref(self, product, vender_profile):
        ref = ProductReference(product=product)
        ref_f = ProductReferenceForm(vender_profile.to_dict(), instance=ref)
        if ref_f.is_valid(): ref_f.save()
        
    def fetch_image(self, product):
        gis = GoogleImageSearch()
        is_cache, gis_images = gis.search(product.model_id)
        
        for gis_image in gis_images:
            if not (gis_image.url.startswith("http://") or gis_image.url.startswith("https://")):
                continue
            if gis_image.width < 640 or gis_image.height < 480:
                continue
            
            product.fetch_image_from_url(gis_image.url)
            return True
        return False
        
    def post(self, request):
        model_id = request.POST.get('model_id')
        group = request.POST.get('group', '')
        price = request.POST.get('price')
        
        if not model_id:
            return {'st': False, 'error': 'No model id given'}
        
        exist_item = Product.objects.filter(model_id=model_id).first()
        if exist_item:
            return {'st': False, 'url': reverse('product', args=(exist_item.id, )), 'message': 'ITEM_ALREADY_EXIST'}
        
        rakuten_vendor = get_vendor('rakuten')()
        rakuten = rakuten_vendor.search(model_id)[-1][0]
        
        amazon_vendor = get_vendor('amazon_jp')()
        amazon = amazon_vendor.search(model_id)[-1][0]
        
        jan = rakuten_vendor.fetch_jan(rakuten.url)
        
        product = Product(manufacturer=amazon.manufacturer, model_id=model_id, group=group,
            release_date=amazon.release_date or rakuten.release_date, weight=amazon.weight,
            size=amazon.size, price=price, summary="", color="", details="",
            jan=jan, created_at=current_local_time_str())
        product.save()
        
        self.write_ref(product, rakuten)
        self.write_ref(product, amazon)
        self.fetch_image(product)
        
        return {'st': True, 'url': reverse('product', args=(product.id, ))}
