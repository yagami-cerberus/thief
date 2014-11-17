
import json
import csv
import os

from tempfile import NamedTemporaryFile
from django.conf import settings

from thief.auction.models import Color

def modify_title(meta):
    title = meta.get('manufacturer') or ''
    model_id = meta.get('model_id') or ''
    summary = meta.get('summary') or ''
    keywords = meta.get('keywords') or ''
    made_at = meta.get('made_at') or ''
    return ' '.join((title, model_id, summary, keywords, made_at)).encode("big5", "ignore")

class BaseRule(object):
    BOOLEAN_FIELDS = []
    
    def get_rule(self, name):
        path = os.path.join(settings.BASE_DIR, "thief", "auction", "csv_rules", "%s.json" % name)
        with open(path) as f:
            return json.load(f)

    def get_fields(self):
        return [f[1] for f in self.rule]

    def get_header(self):
        return [f[0].encode("big5", "ignore") for f in self.rule]
    
    def get_named_to_symbol(self):
        return {f[0]: f[1] for f in self.rule}
    
    def __init__(self, fileobj, mode, type):
        self.rule = self.get_rule(type)
        self.file = fileobj
        self.fields = self.get_fields()
        
        if mode == 'w':
            self.mode = 'w'
            self.csv = csv.writer(self.file)
            self.csv.writerow(self.get_header())
        elif mode == 'r':
            self.mode = 'r'
            self.csv = csv.DictReader(self.file)
    
    def close_write(self):
        self.file.flush()
        return "auction.csv"
    
    def readrows(self):
        symbols = self.get_named_to_symbol()
        
        for raw in self.csv:
            data = {}
            for key, value in raw.items():
                field = symbols.get(key.decode("big5", "ignore"))
                if not field: continue
                else:
                    data[field] = self.csv_2_data(field, value)
            yield data
        
    def writerow(self, meta):
        self.csv.writerow(
            [self.data_2_csv(f, meta) for f in self.fields])
    
    def data_2_csv(self, field, meta):
        return "%s" % meta.get(field)
    
    def csv_2_data(self, field, value):
        if field in self.BOOLEAN_FIELDS:
            if value.startswith("y"): return True
            elif value.startswith("n"): return False
        elif value:
            return value.decode("big5", "ignore")
        else:
            return None

class YahooRule(BaseRule):
    def __init__(self, fileobj, mode):
        BaseRule.__init__(self, fileobj, mode, 'yahoo')

    def close_write(self):
        BaseRule.close_write(self)
        return 'yauctions_batch.csv'

    def data_2_csv(self, field, meta):
        val = meta.get(field)
        if field == "describe":
            if "image_1" in meta:
                return """<center><img src="%s%s"></center>""" % \
                    (meta.get("yahoo_image_url_prefix", ""), meta['image_1'])
        elif field == "title":
            return modify_title(meta)
        
        if val:
            if isinstance(val, unicode):
                return val.encode("big5", "ignore")
            elif isinstance(val, str):
                return val
            elif isinstance(val, bool):
                return val and "yes" or "no"
            elif isinstance(val, (int, float, long)):
                return "%s" % val
            else:
                return "%s" % val
        else:
            return ""
    
class RutenRule(BaseRule):
    def __init__(self, fileobj, mode):
        BaseRule.__init__(self, fileobj, mode, 'ruten')
    
    def close_write(self):
        BaseRule.close_write(self)
        return 'item_rakuten.csv'
        
    def data_2_csv(self, field, meta):
        val = meta.get(field)
        if field == "describe":
            if "image_1" in meta:
                return """<center><img src="%s%s"></center>""" % \
                    (meta.get("ruten_image_url_prefix", ""), meta['image_1'])
        elif field == "title":
            return modify_title(meta)
        
        if val:
            if isinstance(val, unicode):
                return val.encode("big5", "ignore")
            elif isinstance(val, str):
                return val
            elif isinstance(val, bool):
                return val and "y" or "n"
            elif isinstance(val, (int, float, long)):
                return "%s" % val
            else:
                return "%s" % val
        else:
            return ""
    
    def close_write(self):
        BaseRule.close_write(self)
        return 'ruten_auction.csv'

class RakutenRule(BaseRule):
    def __init__(self, fileobj, mode):
        BaseRule.__init__(self, fileobj, mode, 'rakuten')
    
    def data_2_csv(self, field, meta):
        val = meta.get(field)
        if field == "default_0":
            return "0"
        elif field == "default_1":
            return "1"
        elif field == "default_-1":
            return "-1"
        elif field == "home_catalog":
            return u'\u9996\u9801'.encode('big5', 'ignore')
        elif field == "describe":
            if "image_1" in meta:
                return """<center><img src="%s%s"></center>""" % \
                    (meta.get("rakuten_image_url_prefix", ""), meta['image_1'])
        elif field == "title":
            return modify_title(meta)
        
        if field.startswith("product_type_"):
            val = self.product_type_subhandler(field, meta)
            return val.encode('big5', 'ignore')
        
        if val:
            if isinstance(val, unicode):
                return val.encode("big5", "ignore")
            elif isinstance(val, str):
                return val
            elif isinstance(val, bool):
                return val and "y" or "n"
            elif isinstance(val, (int, float, long)):
                return "%s" % val
            else:
                return "%s" % val
        else:
            return ""
    
    def product_type_subhandler(self, field, meta):
        colors = meta['colors']
        
        index = int(field.split('_')[3]) - 1
        
        if index < len(colors):
            if field.endswith("_code"):
                return colors[index]
            elif field.endswith("_label"):
                c = Color.objects.filter(symbol=colors[index]).first()
                if c: return c.name
            elif field == "product_type_1_0":
                return u'\u984f\u8272'
        return ""