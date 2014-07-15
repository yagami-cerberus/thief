from django import forms

class AuctionTypeNoForm(forms.Form):
    no = forms.CharField(max_length=256, label="\xe4\xbb\xa3\xe7\xa2\xbc")
    title = forms.CharField(max_length=1024, label="\xe5\x90\x8d\xe7\xa8\xb1")
