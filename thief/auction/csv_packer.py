from tempfile import mkdtemp
import zipfile
import logging
import shutil
import os

from thief.auction.models import AuctionConfigs
from thief.auction.forms import AuctionConfigsForm
from thief.auction import csv_rules

TEMP_PREFIX = "tmp_auction_"

logger = logging.getLogger(__name__)

class CsvPacker(object):
    def get_csv_engine(self, type):
        if type == 'yahoo':
            return csv_rules.YahooRule(self.csv_file, 'w')
        elif type == 'ruten':
            return csv_rules.RutenRule(self.csv_file, 'w')

    @property
    def archive_path(self):
        return os.path.join(self.tempdir, "archive.zip")

    def __init__(self, auction_type):
        self.tempdir = mkdtemp(prefix=TEMP_PREFIX)
        self.csv_filename = os.path.join(self.tempdir, "table.csv")
        self.csv_file = open(self.csv_filename, "wb")
        
        gf = AuctionConfigsForm({c.key:c.value for c in AuctionConfigs.objects.all()})
        gf.full_clean()
        self.default_data = gf.cleaned_data

        self.csv = self.get_csv_engine(auction_type)
        if not self.csv: raise RuntimeError("Bad auction type")

        self.archive = zipfile.ZipFile(self.archive_path, 'w')

    def pack(self, products):
        for p in products:
            meta, attach_files = p.export()
            meta = dict(self.default_data.items() + meta.items())
            self.csv.writerow(meta)

            for local, archname in attach_files:
                self.archive.write(local, archname)

    def get_fileobject(self):
        archname = self.csv.close_write()
        self.archive.write(self.csv_filename, archname)
        self.archive.close()

        return open(self.archive_path, "rb")

class CsvUnpacker(object):
    def get_csv_engine(self, type):
        if type == 'yahoo':
            return csv_rules.YahooRule(self.csv_file, 'r')
        elif type == 'ruten':
            return csv_rules.RutenRule(self.csv_file, 'r')
    
    def __init__(self, auction_type, file):
        self.csv_file = file
        self.csv = self.get_csv_engine(auction_type)
    
    def load(self):
        return [i for i in self.csv.readrows()]