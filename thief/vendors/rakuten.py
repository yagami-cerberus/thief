
from django.conf import settings

from random import choice
import urllib
import json

from .base import VendorBase, ProductOverview


RAKUTEN_ENDPOINT = "https://app.rakuten.co.jp/services/api/Product/Search/20140305"


class Rakuten(VendorBase):
    vendor_name = "rakuten"
    
    def __init__(self):
        self.conf = choice(settings.RAKUTEN_KEYS)
    
    def _search(self, keyword):
        qs = urllib.urlencode({
            "format": "json",
            "applicationId": self.conf["applicationId"],
            "developerId": self.conf["applicationId"],
            "affiliateId": self.conf["affiliateId"],
            "keyword": keyword
        })
        req = urllib.urlopen(RAKUTEN_ENDPOINT + "?" + qs)
        doc = json.load(req)
        
        if 'error' in doc:
            raise RuntimeError(doc['error'], doc['error_description'])
        
        return tuple(self.load_overview(i['Product']) for i in doc['Products'])
        
    def load_overview(self, r):
        return ProductOverview(self.vendor_name, r.ASIN.text,
            r['productName'],
            url=r.get('productUrlPC'),
            currency='Yen',
            price=r.get('averagePrice') or r.get('minPrice') or r.get('salesMinPrice'),
            ean=get_ean(r),
            release_date=get_release_date(r),
            weight=get_weight(r),
            size=get_size(r)
        )