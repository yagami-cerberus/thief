from django.test import TestCase

from thief.vendor.amazon import AmazonJP

# Create your tests here.
class AmazonJP_Test(TestCase):
    def test_search(self):
        amazon = AmazonJP()
        results = amazon.search("Nanoha")
