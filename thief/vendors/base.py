
import abc
from abc import ABCMeta

from thief.vendors.models import Cache

class VendorBase(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def _search(self, keyword):
        pass
    
    def search(self, keyword):
        keyword = keyword.strip()
        cache = Cache.get_cache(self.vendor_name, 'search', keyword)
        if cache:
            return (True, [ProductOverview.from_dict(row) for row in cache])
        else:
            results = self._search(keyword)
            cache = Cache.set_cache(self.vendor_name, 'search', keyword, [
                r.to_dict() for r in results
            ])
            return (False, results)
            
    # @abc.abstractmethod
    # def _details(self, item_id):
    #     pass

class ProductOverview(object):
    def __init__(self, vendor, item_id, title, **kw):
        self.vendor = vendor
        self.item_id = item_id
        self.title = title
        
        self.url = kw.get('url')
        self.currency = kw.get('currency')
        self.price = kw.get('price')
        self.ean = kw.get('ean')
        self.release_date = kw.get('release_date')
        self.weight = kw.get('weight')
        self.size = kw.get('size')
        self.manufacturer = kw.get('manufacturer')
    
    def to_dict(self):
        data = {'vendor': self.vendor, 'item_id': self.item_id, 'title': self.title}
        
        if self.url: data['url'] = self.url
        if self.currency: data['currency'] = self.currency
        if self.price: data['price'] = self.price
        if self.ean: data['ean'] = self.ean
        if self.release_date: data['release_date'] = self.release_date
        if self.weight: data['weight'] = self.weight
        if self.size: data['size'] = self.size
        if self.manufacturer: data['manufacturer'] = self.manufacturer
        
        return data
    
    @classmethod
    def from_dict(cls, doc):
        if 'vendor' not in doc: doc['vendor'] = ''
        if 'item_id' not in doc: doc['item_id'] = ''
        if 'title' not in doc: doc['title'] = ''
        
        return cls(**doc)
        
    def __repr__(self):
        return (u"<%s:%s # %s>" % (self.vendor, self.item_id, self.title)).encode('utf8')

