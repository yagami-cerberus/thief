from django import forms

from thief.products import models

class Product(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['title', 'model_id', 'group', 'jan', 'release_date',
            'keywords', 'summary', 'size', 'weight', 'price', 'amount', 'color', 'details', 'usage_status', 'yahoo_no', 'ruten_no']
        exclude = ('product', 'vendor', 'item_id', 'source_price', 'source_currency')

class ProductReference(forms.ModelForm):
    class Meta:
        exclude = ('product', )
        model = models.ProductReference