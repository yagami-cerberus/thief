from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from thief.rest import ThiefREST

from thief.auction.models import YahooProductNo, RutenProductNo
from thief.auction.forms import AuctionTypeNoForm

AUCTION_TYPE = {
    'yahoo': YahooProductNo,
    'ruten': RutenProductNo
}

def auction_types(request, type):
    model = AUCTION_TYPE[type]
    records = model.objects.order_by('title').all()
    return render(request, 'auction_types.html', {
        'items': records,
        'type': type,
        'cls': model
    })

class create_auction_type(ThiefREST):
    template = 'create_auction_type.html'
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
    template = 'edit_auction_type.html'
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
    
# def auction_new(request, type):
#     render('new.html', request)
    
# def auction_edit()