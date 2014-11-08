
from django.conf import settings
from random import choice
import urllib
import json

from thief.vendors.models import Cache

"""
Note:
    Google search references:
    https://developers.google.com/custom-search/json-api/v1/using_rest#api-specific_query_parameters
"""

GOOGLE_END_POINT = "https://www.googleapis.com/customsearch/v1"

class GoogleImageSearch(object):
    vendor_name = "google"
    
    def __init__(self):
        self.conf = choice(settings.GOOGLE_CUSTOM_SEARCH_API_KEYS)
    
    def raw_search(self, keyword):
        qs = urllib.urlencode({
            "key": self.conf[0],
            "cx": self.conf[1],
            "searchType":"image",
            # "imgSize": "huge",
            "gl": "ja",
            "hl": "ja-jp",
            "googlehost": "google.co.jp",
            "lr": "lang_ja",
            "q": keyword
        })
        
        req = urllib.urlopen(GOOGLE_END_POINT + "?" + qs)
        return json.load(req)

    def _search(self, keyword):
        doc = self.raw_search(keyword)
        return [self.load_result(keyword, i) for i in doc.get('items', ())]
    
    def search(self, keyword, allow_cache=True):
        keyword = keyword.encode("utf8").strip()
        
        cache = None
        if allow_cache:
            cache = Cache.get_cache(self.vendor_name, 'search', keyword)
        
        if cache:
            return (True, [GoogleImageSearchResult.from_dict(row) for row in cache])
        else:
            results = self._search(keyword)
            Cache.set_cache(self.vendor_name, 'search', keyword, [
                r.to_dict() for r in results
            ])
            return (False, results)
        
    def load_result(self, keyword, r):
        return GoogleImageSearchResult(keyword,
            r['link'],
            r['image']['thumbnailLink'],
            r['title'],
            width=int(r['image']['width']),
            height=int(r['image']['height'])
        )
                
class GoogleImageSearchResult(object):
    def __init__(self, keyword, url, thumb_url, title, **kw):
        self.keyword = keyword
        self.url = url
        self.thumb_url = thumb_url
        self.title = title
        self.width = kw.get('width', 0)
        self.height = kw.get('height', 0)
    
    def to_dict(self):
        data = {'keyword': self.keyword, 'url': self.url, 'thumb_url': self.thumb_url, 'title': self.title,
            'width': self.width, 'height': self.height}
        return data
    
    @classmethod
    def from_dict(cls, doc):
        return cls(**doc)
    
    def __repr__(self):
        return ("<GoogleImageResult:%s # %s>" %(self.title, self.url)).encode("utf8")
    
