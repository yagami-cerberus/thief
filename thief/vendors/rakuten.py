
from django.conf import settings

from random import choice
import urllib
import json

import re

from .base import VendorBase, ProductOverview


RAKUTEN_ENDPOINT = "https://app.rakuten.co.jp/services/api/Product/Search/20140305"

WEIGHT_PATTERN = re.compile("[0-9,\.]+\s*k?g", re.IGNORECASE)

def find_weight(keyvalues):
    if not keyvalues: return ""

    for item in keyvalues:
        if "detail" in item:
            d = item["detail"]
            name = item.get("name") or ""
            value = item.get("value") or ""
            m = WEIGHT_PATTERN.search(value)
            if m: return m.group()

    return ""
    
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
            "keyword": keyword.encode('utf8')
        })
        req = urllib.urlopen(RAKUTEN_ENDPOINT + "?" + qs)
        doc = json.load(req)
        
        if 'error' in doc:
            raise RuntimeError(doc['error'], doc['error_description'])
        
        return tuple(self.load_overview(i['Product']) for i in doc['Products'])
        
    def load_overview(self, r):
        return ProductOverview(self.vendor_name, r['productId'],
            r['productName'],
            url=r.get('productUrlPC'),
            currency='JPN',
            price=r.get('averagePrice') or r.get('minPrice') or r.get('salesMinPrice'),
            ean="",
            release_date='',
            manufacturer=r.get('makerNameFormal'),
            weight=find_weight(r.get('ProductDetails')),
            size='',
        )