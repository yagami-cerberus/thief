from django.core.management.base import BaseCommand
from thief.vendors import get_vendor

class Command(BaseCommand):
    args = 'vendor_name keyword'
    
    def handle(self, vendor_name, keyword, **options):
        vendor_cls = get_vendor(vendor_name)
        vendor = vendor_cls()
        is_cache, results = vendor.search(keyword)
        print("Use cache: %s\n" % is_cache)
        for r in results:
            print(r)
            print(r.url)
            print("="*70)