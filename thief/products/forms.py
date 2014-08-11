from django import forms

from thief.products import models
from thief.auction.forms import KeywordGroupWidget

class Product(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['title', 'model_id', 'group', 'jan', 'release_date',
            'keywords', 'summary', 'size', 'weight', 'price', 'amount',
            'color', 'details', 'usage_status', 'yahoo_no', 'ruten_no',
            'rakuten_no']
        exclude = ('product', 'vendor', 'item_id', 'source_price', 'source_currency')
        widgets = {
            'group': KeywordGroupWidget
        }
    
class ProductReference(forms.ModelForm):
    class Meta:
        exclude = ('product', )
        model = models.ProductReference
