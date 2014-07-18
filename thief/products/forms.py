from django import forms

from thief.products import models

class Product(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['title', 'yahoo_no', 'ruten_no', 'ean', 'release_date',
            'keywords', 'summary', 'price', 'amount', 'color', 'details', 'usage_status']
        exclude = ('product', 'vendor', 'item_id', 'source_price', 'source_currency')
        