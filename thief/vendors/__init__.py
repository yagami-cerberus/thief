
from .google_image_search import GoogleImageSearch
from .rakuten import Rakuten
from .amazon import AmazonJP
from .base import ProductOverview

vendors = (AmazonJP, Rakuten, GoogleImageSearch)

def get_vendor(vendor_name):
    for v in vendors:
        if v.vendor_name == vendor_name:
            return v
    raise RuntimeError("Bad vendor name: %s" % vendor_name)
