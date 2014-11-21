
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
        mi, gi, pi = 0, 1, 2
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
        is_cache, gis_images = gis.search("%s %s" % (product.model_id, manufacturer))
        
        for gis_image in gis_images:
            if not (gis_image.url.startswith("http://") or gis_image.url.startswith("https://")):
                continue
            if gis_image.width < 640 or gis_image.height < 480:
                continue
            
            product.fetch_image_from_url(gis_image.url)
            return True
        return False
    
    def guess_keywords(self, p):
        g = Product.objects.filter(group=p.group, keywords__isnull=False).exclude(id=p.id, keywords="").order_by("-id").first()
        if g:
            return g.keywords

    def manufacturer_convert(self, orig_input):
        m = {
            "\xe3\x83\xa4\xe3\x83\x9e\xe3\x83\x8f\xe6\xa0\xaa\xe5\xbc\x8f\xe4\xbc\x9a\xe7\xa4\xbe": "YAMAHA",
            "\xe3\x83\xa4\xe3\x83\x9e\xe3\x83\x8f": "YAMAHA",
            "\xe3\x83\x91\xe3\x83\x8a\xe3\x82\xbd\xe3\x83\x8b\xe3\x83\x83\xe3\x82\xaf": "Panasonic",
            "\xe3\x82\xbd\xe3\x83\x8b\xe3\x83\xbc\xe6\xa0\xaa\xe5\xbc\x8f\xe4\xbc\x9a\xe7\xa4\xbe": "SONY",
            "\xe3\x82\xbd\xe3\x83\x8b\xe3\x83\xbc": "SONY",
            "\xe3\x82\xb7\xe3\x83\xa3\xe3\x83\xbc\xe3\x83\x97\xe6\xa0\xaa\xe5\xbc\x8f\xe4\xbc\x9a\xe7\xa4\xbe": "Sharp",
            "\xe3\x82\xb7\xe3\x83\xa3\xe3\x83\xbc\xe3\x83\x97": "Sharp",
            "\xe3\x82\xab\xe3\x82\xb7\xe3\x82\xaa\xe8\xa8\x88\xe7\xae\x97\xe6\xa9\x9f": "CASIO",
            "\xe3\x82\xab\xe3\x82\xb7\xe3\x82\xaa": "CASIO",
            "\xe3\x83\x80\xe3\x82\xa4\xe3\x83\x8b\xe3\x83\x81\xe5\xb7\xa5\xe6\xa5\xad\xe6\xa0\xaa\xe5\xbc\x8f\xe4\xbc\x9a\xe7\xa4\xbe": "DAINICHI",
            "\xe3\x83\x80\xe3\x82\xa4\xe3\x83\x8b\xe3\x83\x81": "DAINICHI",
            "\xe6\xa0\xaa\xe5\xbc\x8f\xe4\xbc\x9a\xe7\xa4\xbe\xe3\x83\xaf\xe3\x82\xb3\xe3\x83\xa0": "Wacom",
            "\xe3\x83\xaf\xe3\x82\xb3\xe3\x83\xa0": "Wacom",
            "\xe3\x83\xaf\xe3\x82\xb3\xe3\x83\xa0\xe6\xa0\xaa\xe5\xbc\x8f\xe4\xbc\x9a\xe7\xa4\xbe": "Wacom",
            
        }
        return m.get(orig_input, orig_input)
    
    def post(self, request):
        model_id = request.POST.get('model_id')
        group = request.POST.get('group', '')
        price = request.POST.get('price')
        
        if not model_id:
            return {'st': False, 'error': 'No model id given'}
        
        exist_item = Product.objects.filter(model_id=model_id).first()
        if exist_item:
            return {'st': False, 'url': reverse('product', args=(exist_item.id, )), 'message': 'ITEM_ALREADY_EXIST'}
        
        rakuten = self._shallow_result
        amazon = self._shallow_result
        jan = ""
        
        try:
            rakuten_vendor = get_vendor('rakuten')()
            rakuten = rakuten_vendor.search(model_id)[-1][0]
            jan = rakuten_vendor.fetch_jan(rakuten.url)
        except IndexError:
            pass
        
        try:
            amazon_vendor = get_vendor('amazon_jp')()
            amazon = amazon_vendor.search(model_id)[-1][0]
        except IndexError:
            pass
        
        product = Product(manufacturer=self.manufacturer_convert(amazon.manufacturer),
            model_id=model_id, group=group, release_date=amazon.release_date or rakuten.release_date,
            weight=amazon.weight, size=amazon.size, price=price, summary="", color="", details="",
            jan=jan, created_at=current_local_time_str())
        
        product.keywords = self.guess_keywords(product)
        product.save()

        if not isinstance(rakuten, self.Shallow): self.write_ref(product, rakuten)
        if not isinstance(amazon, self.Shallow): self.write_ref(product, amazon)
        self.fetch_image(product)
        
        return {'st': True, 'url': reverse('product', args=(product.id, ))}
