from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from thief.rest import ThiefREST

from thief.auction.models import YahooProductNo, RutenProductNo, AuctionConfigs, Keyword
from thief.auction.forms import AuctionTypeNoForm, AuctionConfigsForm

AUCTION_TYPE = {
    'yahoo': YahooProductNo,
    'ruten': RutenProductNo
}

class global_configs(ThiefREST):
    template = 'auction/configs.html'

    def get(self, request):
        form = AuctionConfigsForm({c.key:c.value for c in AuctionConfigs.objects.all()})
        return {'form': form}

class edit_global_configs(ThiefREST):
    template = 'auction/edit_configs.html'
    
    def get(self, request):
        form = AuctionConfigsForm(initial={c.key:c.value for c in AuctionConfigs.objects.all()})
        return {'form': form}

    def post(self, request):
        form = AuctionConfigsForm(request.POST)

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

class keywords(ThiefREST):
    template = 'auction/keywords.html'

    def get(self, request):
        return {'keywords': Keyword.objects.order_by('pk').all()}

    def post(self, request):
        keyword = request.POST.get('k')
        if len(Keyword.objects.filter(keyword=keyword)) == 0:
            Keyword(keyword=keyword).save()
        return redirect(reverse('auction_keywords'))

    def delete(self, request):
        pk = request.POST.get('pk')
        for k in Keyword.objects.filter(pk=pk):
            k.delete()
        return redirect(reverse('auction_keywords'))

class auction_types(ThiefREST):
    template = 'auction/auction_types.html'

    def get(self, request, type):
        model = AUCTION_TYPE[type]
        records = model.objects.order_by('title').all()
        return {'items': records, 'type': type, 'cls': model}

class create_auction_type(ThiefREST):
    template = 'auction/create_auction_type.html'
    def get(self, request, type):
        model = AUCTION_TYPE[type]
        return {'form': AuctionTypeNoForm(), 'type': type}
    
    def post(self, request, type):
        model = AUCTION_TYPE[type]
        form = AuctionTypeNoForm(request.POST)
        
        if form.is_valid():
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
        form = AuctionTypeNoForm(initial={'no': record.no, 'title': record.title})
        return {'form': form, 'type': type}

    def post(self, request, type, id):
        model = AUCTION_TYPE[type]
        form = AuctionTypeNoForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            record = model.objects.get(id=id)
            record.no = data['no']
            record.title = data['title']
            record.save()
            return redirect(reverse('auction_types', args=(type, )))
        else:
            return {'form': form, 'type': type}
    
class delete_auction_type(ThiefREST):
    def post(self, request, type):
        model = AUCTION_TYPE[type]
        form = AuctionTypeNoForm(request.POST)
        id = request.POST.get('id')
        record = model.objects.get(id=id)
        record.delete()
        return redirect(reverse('auction_types', args=(type, )))

