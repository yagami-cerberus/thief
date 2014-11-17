from django.utils.crypto import get_random_string
from django.template.loader import get_template
from django.utils.html import format_html
from django.template import Context
from django import forms

from thief.auction import models

class KeywordGroupWidget(forms.HiddenInput):
    is_hidden = False
    
    def render(self, name, value, attrs=None):
        if not attrs: attrs = {}
        id = get_random_string(8)
        attrs['data-kgw-id'] = id
        input = super(KeywordGroupWidget, self).render(name, value, attrs)
        
        t = get_template("auction/__keyword_dropdown_selector.html")
        return t.render(Context({
            'keyword_groups': [{"id": g, "text": g} for g in models.Keyword.get_groups()],
            'input': input,
            'small': ("input-sm" in attrs.get("class", "")),
            'input_selector': 'input[data-kgw-id=%s]' % (id, ),
            'identify': get_random_string(6)}))

class MultiColorWidget(forms.SelectMultiple):
    def render(self, name, value, attrs=None):
        if not attrs: attrs = {}
        id = get_random_string(8)
        attrs['data-kgw-id'] = id
        input = super(MultiColorWidget, self).render(name, value, attrs,
             choices=models.Color.objects.values_list("symbol", "name"))
        
        t = get_template("auction/__color_multi_selector.html")
        return t.render(Context({
            'input': input,
            'small': ("input-sm" in attrs.get("class", "")),
            'input_selector': 'select[data-kgw-id=%s]' % (id, )}))

class AuctionTypeNoForm(forms.Form):
    no = forms.CharField(max_length=256, label="\xe4\xbb\xa3\xe7\xa2\xbc")
    title = forms.CharField(max_length=1024, label="\xe5\x93\x81\xe9\xa0\x85", widget=KeywordGroupWidget)

class AuctionConfigsForm(forms.Form):
    goods_location = forms.CharField(label='\xe7\x89\xa9\xe5\x93\x81\xe6\x89\x80\xe5\x9c\xa8\xe5\x9c\xb0', required=False)
    
    auction_duration = forms.IntegerField(label='\xe6\x8b\x8d\xe8\xb3\xa3\xe6\x9c\x9f\xe9\x96\x93', required=False)
    auction_end_at = forms.IntegerField(label='\xe7\xb5\x90\xe6\x9d\x9f\xe6\x99\x82\xe9\x96\x93', required=False)
    auto_expend = forms.NullBooleanField(label='\xe8\x87\xaa\xe5\x8b\x95\xe5\xbb\xb6\xe9\x95\xb7', required=False)
    reopen_amount = forms.IntegerField(label='\xe9\x87\x8d\xe6\x96\xb0\xe5\x88\x8a\xe7\x99\xbb\xe6\xac\xa1\xe6\x95\xb8', required=False)
    end_advance = forms.NullBooleanField(label='\xe6\x8f\x90\xe5\x89\x8d\xe7\xb5\x90\xe6\x9d\x9f')
    
    pay__4 = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x977-11\xe4\xbb\x98\xe6\xac\xbe')
    pay_fami = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe5\x85\xa8\xe5\xae\xb6\xe4\xbb\x98\xe6\xac\xbe')
    pay_atm = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97 ATM \xe8\xbd\x89\xe5\xb8\xb3\xe4\xbb\x98\xe6\xac\xbe')
    pay_meet = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe9\x9d\xa2\xe4\xba\xa4 (\xe9\x9c\xb2\xe5\xa4\xa9)')
    pay_card = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe4\xbf\xa1\xe7\x94\xa8\xe5\x8d\xa1')
    pay_car_x3 = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe4\xbf\xa1\xe7\x94\xa8\xe5\x8d\xa1\xe5\x88\x86\xe6\x9c\x9f: 3 (yahoo)')
    pay_car_x6 = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe4\xbf\xa1\xe7\x94\xa8\xe5\x8d\xa1\xe5\x88\x86\xe6\x9c\x9f: 6 (yahoo)')
    pay_car_x12 = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe4\xbf\xa1\xe7\x94\xa8\xe5\x8d\xa1\xe5\x88\x86\xe6\x9c\x9f: 12 (yahoo)')
    pay_car_x24 = forms.NullBooleanField(label='\xe6\x8e\xa5\xe5\x8f\x97\xe4\xbf\xa1\xe7\x94\xa8\xe5\x8d\xa1\xe5\x88\x86\xe6\x9c\x9f: 24 (yahoo)')

    shipping_postoffice = forms.IntegerField(label='\xe9\x81\x8b\xe8\xb2\xbb: \xe9\x83\xb5\xe5\xaf\x84', required=False)
    shipping_freight = forms.IntegerField(label='\xe9\x81\x8b\xe8\xb2\xbb: \xe8\xb2\xa8\xe9\x81\x8b  (\xe9\x9c\xb2\xe5\xa4\xa9)', required=False)
    shipping_kuroneko = forms.IntegerField(label='\xe9\x81\x8b\xe8\xb2\xbb: \xe5\xae\x85\xe9\x85\x8d', required=False)
    merge_shipping = forms.NullBooleanField(label='\xe5\x90\x88\xe4\xbd\xb5\xe9\x81\x8b\xe8\xb2\xbb')

    ban_lowest_rating = forms.IntegerField(label='\xe9\x99\x90\xe5\x88\xb6\xe4\xb8\x8b\xe6\xa8\x99\xe6\x9c\x80\xe4\xbd\x8e\xe8\xa9\x95\xe5\x83\xb9', required=False)
    ban_bad_rating = forms.IntegerField(label='\xe9\x99\x90\xe5\x88\xb6\xe4\xb8\x8b\xe6\xa8\x99\xe8\xb2\xa0\xe8\xa9\x95\xe5\x83\xb9\xe6\x95\xb8', required=False)
    
    amount = forms.IntegerField(label='\xe6\x95\xb8\xe9\x87\x8f', required=False)
    usage_status = forms.CharField(label='\xe7\x89\xa9\xe5\x93\x81\xe6\x96\xb0\xe8\x88\x8a', max_length=255, required=False)
    made_at = forms.CharField(label='\xe7\x94\xa2\xe5\x9c\xb0', required=False)
    
    yahoo_image_url_prefix = forms.CharField(label='yahoo\xe5\x9c\x96\xe7\x89\x87\xe7\xb6\xb2\xe5\x9d\x80prefix', required=False)
    ruten_image_url_prefix = forms.CharField(label='ruten\xe5\x9c\x96\xe7\x89\x87\xe7\xb6\xb2\xe5\x9d\x80prefix', required=False)
    rakuten_image_url_prefix = forms.CharField(label='rakuten\xe5\x9c\x96\xe7\x89\x87\xe7\xb6\xb2\xe5\x9d\x80prefix', required=False)
