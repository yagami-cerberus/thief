from django import forms

from thief.products import models
from thief.auction.forms import KeywordGroupWidget, MultiColorWidget

class MultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass

class Product(forms.ModelForm):
    colors_meta = MultipleChoiceField(widget=MultiColorWidget)
    
    class Meta:
        model = models.Product
        fields = ['manufacturer', 'model_id', 'group', 'jan', 'release_date',
            'keywords', 'summary', 'size', 'weight', 'price', 'color',
            'details', 'colors_meta', 'created_at']
        exclude = ('product', 'vendor', 'item_id', 'source_price', 'source_currency')
        widgets = {
            'group': KeywordGroupWidget,
            'colors_meta': MultiColorWidget,
        }
    
    
class ProductReference(forms.ModelForm):
    class Meta:
        exclude = ('product', )
        model = models.ProductReference
