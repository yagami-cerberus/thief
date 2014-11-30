from django import forms

from thief.products import models
from thief.auction.forms import CatalogWidget, KeywordWidget, MultiColorWidget

class MultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass

class Product(forms.ModelForm):
    colors_meta = MultipleChoiceField(widget=MultiColorWidget)
    
    class Meta:
        model = models.Product
        fields = ['catalog', 'manufacturer', 'model_id', 'keywords', 'jan', 
            'release_date', 'summary', 'size', 'weight', 'price', 'details',
            'colors_meta', 'created_at']
        exclude = ('product', 'vendor', 'item_id', 'source_price', 'source_currency')
        widgets = {
            'catalog': CatalogWidget,
            'keywords': KeywordWidget,
            'colors_meta': MultiColorWidget,
        }
    
    
class ProductReference(forms.ModelForm):
    class Meta:
        exclude = ('product', )
        model = models.ProductReference
