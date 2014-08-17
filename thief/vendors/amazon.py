
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
def get_manufacturer(r):
    return r.ItemAttributes.Manufacturer.text
    
@ignore_attribute_error
def get_release_date(r):
    return r.ItemAttributes.ReleaseDate.text

@ignore_attribute_error
def get_weight(r):
    tw = r.ItemAttributes.PackageDimensions.Weight.text
    tu = r.ItemAttributes.PackageDimensions.Weight.get('Units')
    
    if tu == 'hundredths-pounds':
        try:
            w = float(tw) * 0.0045359237
            if w < 0.9:
                return "%.1f g" % (w * 1000)
            else:
                return "%.2f kg" % w
        except ValueError:
            pass
    
    return '%s %s' % (tw, tu)

@ignore_attribute_error
def get_size(r):
    th = r.ItemAttributes.PackageDimensions.Height.text
    tl = r.ItemAttributes.PackageDimensions.Length.text
    tw = r.ItemAttributes.PackageDimensions.Width.text
    tu = r.ItemAttributes.PackageDimensions.Height.get('Units')
    
    if tu == 'hundredths-inches':
        try:
            h, l, w = float(th), float(tl), float(tw)
            return '%.1fx%.1fx%.1f cm' % (w * 0.0254, l * 0.0254, h * 0.0254)
        except ValueError:
            pass
    
    return '%sx%sx%s %s' % (th, tl, tw, tu)

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
