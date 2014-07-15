from django import forms

from thief.products import models

class Product(forms.ModelForm):
    class Meta:
        model = models.Product

class ProductMeta(forms.ModelForm):
    class Meta:
        model = models.ProductMeta
        exclude = ('product', )
