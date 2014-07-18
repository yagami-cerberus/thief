

from thief.rest import ThiefREST, ThiefRestAPI
from thief.vendors import get_vendor

class search_product(ThiefREST):
	template = 'search_product.html'

	def get(self, request):
		return {}

class query_vendor(ThiefRestAPI):
    def get(self, request):
        vendor_cls = get_vendor(request.GET.get('vendor_name'))
        vendor = vendor_cls()
        is_cache, results = vendor.search(request.GET.get('keyword'))
    
        return {'status': True, 'is_cache': is_cache,
            'results': [r.to_dict() for r in results[:10]]}

