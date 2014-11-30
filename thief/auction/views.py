from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from thief.rest import ThiefREST, ThiefRestAPI

from thief.auction.models import YahooProductNo, RutenProductNo, RakutenProductNo, AuctionConfigs
from thief.auction.models import Catalog, Keyword, KeywordSet, Color
from thief.auction import forms

AUCTION_TYPE = {
    'yahoo': YahooProductNo,
    'ruten': RutenProductNo,
    'rakuten': RakutenProductNo
}

class global_configs(ThiefREST):
    template = 'auction/configs.html'

    def get(self, request):
        form = forms.AuctionConfigsForm({c.key:c.value for c in AuctionConfigs.objects.all()})
        return {'form': form}

class edit_global_configs(ThiefREST):
    template = 'auction/edit_configs.html'
    
    def get(self, request):
        form = forms.AuctionConfigsForm(initial={c.key:c.value for c in AuctionConfigs.objects.all()})
        return {'form': form}

    def post(self, request):
        form = forms.AuctionConfigsForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            for key, value in data.items():
                self.update_config(key, value)

            return redirect(reverse('auction_configs'))
        else:
            return {'form': form}

    def update_config(self, key, value):
        ms = AuctionConfigs.objects.filter(key=key)
        l = len(ms)
        if l == 1:
            m = ms[0]
            m.value = value or ""
            m.save()
            return m

        if l > 1:
            for z in m: z.delete()

        m = AuctionConfigs(key=key, value=value or "")
        m.save()
        return m

class colors(ThiefREST):
    template = 'auction/colors.html'
    
    def get(self, request):
        return {
            'colors': Color.objects.all()
        }
    
    def post(self, request):
        c = Color(name=request.POST.get('name'), symbol=request.POST.get('symbol'))
        c.save()
        return redirect(reverse('auction_colors'))
    
    def delete(self, request):
        try:
            c = Color.objects.get(pk=request.POST.get('pk'))
            c.delete()
        except Color.DoesNotExist:
            pass
        
        return redirect(reverse('auction_colors'))
        
class auction_types(ThiefREST):
    template = 'auction/auction_types.html'

    def get(self, request, type):
        auction_cls = AUCTION_TYPE[type]
        
        grouped_items = {c: auction_cls.objects.filter(catalog=c).order_by("manufacturer") for c in Catalog.objects.all()}
        return {'grouped_items': grouped_items, 'type': type, 'cls': auction_cls}

class create_auction_type(ThiefREST):
    template = 'auction/create_auction_type.html'
    def get(self, request, type):
        model = AUCTION_TYPE[type]
        default_catalog = Catalog.objects.filter(id=request.GET.get("catalog")).first()
        return {'form': forms.AuctionTypeNoForm(initial={"catalog":default_catalog}), 'type': type}

    def post(self, request, type):
        model = AUCTION_TYPE[type]
        form = forms.AuctionTypeNoForm(request.POST)
        
        if form.is_valid():
            # Note: form.save() can not be use because form model
            #       is an abstract model
            data = form.cleaned_data
            record = model(**data)
            record.save()
            return redirect(reverse('auction_types', args=(type, )))
        else:
            return {'form': form, 'type': type}

class edit_auction_type(ThiefREST):
    template = 'auction/edit_auction_type.html'

    def get(self, request, type, id):
        model = AUCTION_TYPE[type]
        record = model.objects.get(id=id)
        form = forms.AuctionTypeNoForm(instance=record)
        return {'form': form, 'type': type}

    def post(self, request, type, id):
        model = AUCTION_TYPE[type]
        record = model.objects.get(id=id)
        form = forms.AuctionTypeNoForm(request.POST, instance=record)
        
        if form.is_valid():
            form.save()
            return redirect(reverse('auction_types', args=(type, )))
            
        else:
            return {'form': form, 'type': type}
    
class delete_auction_type(ThiefREST):
    def post(self, request, type):
        model = AUCTION_TYPE[type]
        form = forms.AuctionTypeNoForm(request.POST)
        id = request.POST.get('id')
        record = model.objects.get(id=id)
        record.delete()
        return redirect(reverse('auction_types', args=(type, )))

class catalogs(ThiefREST):
    template = 'auction/catalogs.html'

    def get(self, request):
        return {'catalogs': Catalog.objects.all()}
    
    def post(self, request):
        name = request.POST.get("n")
        if name:
            Catalog(name=name).save()
        return redirect(reverse('catalogs'))
    
    def put(self, request):
        c = Catalog.objects.get(id=request.POST.get('id'))
        c.name = request.POST.get('name')
        c.save()
        return redirect(reverse('catalogs'))
    
    def delete(self, request):
        c = Catalog.objects.get(id=request.POST.get('id'))
        c.delete()
        return redirect(reverse('catalogs'))

class keywords(ThiefREST):
    template = 'auction/keywords.html'
    
    def get(self, request, catalog_id):
        catalog = Catalog.objects.get(id=catalog_id)

        return {
            'catalog': catalog,
            'grouped_keywords': catalog.grouped_keywords(),
            'sets': KeywordSet.objects.filter(catalog=catalog)
        }
    
    def post(self, request, catalog_id):
        catalog = Catalog.objects.get(id=catalog_id)
        m, k = request.POST.get('m'), request.POST.get('k')
        
        if k:
            Keyword(catalog=catalog, manufacturer=m, keyword=k).save()
        
        return redirect(reverse('keywords', args=(catalog_id,)))
    
    def delete(self, request, catalog_id):
        for k in Keyword.objects.filter(id=request.POST.get("id"), catalog_id=catalog_id):
            k.delete()

        return redirect(reverse('keywords', args=(catalog_id,)))

class get_keywords(ThiefRestAPI):
    def get(self, request):
        o = (Keyword.objects.filter(catalog_id=request.GET.get("catalog_id")) & 
            (Keyword.objects.filter(manufacturer=request.GET.get("manufacturer")) |
            Keyword.objects.filter(manufacturer=request.GET.get("")))).values_list("keyword", flat=True)
        return list(o)