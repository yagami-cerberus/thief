
import os

from amazonproduct import API, TooManyRequests

from .base import VendorBase, ProductOverview

__all__ = ["AmazonJP"]

# Develope informations:
#     http://associates-amazon.s3.amazonaws.com/signed-requests/helper/index.html

# parse macros
def ignore_attribute_error(fn):
    def wrap(r):
        try:
            return fn(r)
        except AttributeError:
            return None
    return wrap
    
@ignore_attribute_error
def get_url(r):
    return r.DetailPageURL.text

@ignore_attribute_error
def get_currency(r):
    try:
        return r.ItemAttributes.ListPrice.CurrencyCode.text
    except AttributeError:
        return r.OfferSummary.LowestNewPrice.CurrencyCode.text

@ignore_attribute_error
def get_price(r):
    try:
        return r.ItemAttributes.ListPrice.Amount.text
    except AttributeError:
        return r.OfferSummary.LowestNewPrice.Amount.text

@ignore_attribute_error
def get_ean(r):
    return r.ItemAttributes.EAN.text

@ignore_attribute_error
def get_manufacturer(r):
    return r.ItemAttributes.Manufacturer.text
    
@ignore_attribute_error
def get_release_date(r):
    return r.ItemAttributes.ReleaseDate.text

@ignore_attribute_error
def get_weight(r):
    w = r.ItemAttributes.PackageDimensions.Weight.text
    u = r.ItemAttributes.PackageDimensions.Weight.get('Units')
    return w + ' ' + u

@ignore_attribute_error
def get_size(r):
    h = r.ItemAttributes.PackageDimensions.Height.text
    l = r.ItemAttributes.PackageDimensions.Length.text
    w = r.ItemAttributes.PackageDimensions.Width.text
    u = r.ItemAttributes.PackageDimensions.Height.get('Units')
    return h + 'x' + l + 'x' + w + ' ' + u

@ignore_attribute_error
def get_manufacturer(r):
    return r.ItemAttributes.Manufacturer

class Amazon(VendorBase):
    vendor_name = "amazon"
    
    def __init__(self, access_key, secret_key, region):
        self._api = API(access_key_id=access_key, secret_access_key=secret_key, locale=region)
    
    def _search(self, keyword):
        raw_results = self._api.item_search('All', Keywords=keyword, AssociateTag='..', ResponseGroup='ItemAttributes,OfferSummary')
        results = tuple(self.load_overview(r) for r in raw_results)
        return results
    
    def load_overview(self, r):
        return ProductOverview(self.vendor_name, r.ASIN.text,
            r.ItemAttributes.Title.text,
            url=get_url(r),
            currency=get_currency(r),
            price=get_price(r),
            ean=get_ean(r),
            release_date=get_release_date(r),
            weight=get_weight(r),
            size=get_size(r)
        )
    
    def _details(self, item_id):
        return ""

class AmazonJP(Amazon):
    vendor_name = "amazon_jp"
    
    def __init__(self):
        Amazon.__init__(self, os.environ['AWS_ACCESS_KEY'],
            os.environ['AWS_SECRET_KEY'].encode(), 'jp')
