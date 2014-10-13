from django.utils.crypto import get_random_string
from django.template.loader import get_template
from django.template import Context
from django import template

from thief.auction.models import Keyword, KeywordSet
from thief.auction.forms import KeywordGroupWidget

register = template.Library()

@register.simple_tag(name='load_keyword_groups', takes_context=True)
def load_keyword_groups(context):
    context['keyword_groups'] = Keyword.get_groups()
    return ""

@register.simple_tag(name='group_dropdown_selector')
def group_dropdown_selector(name, value, css=""):
    return KeywordGroupWidget().render(name, value, {"class": css} )
    
@register.simple_tag(name='keyword_group_dropdown_selector')
def keyword_group_dropdown_selector(input_selector):
    t = get_template("auction/__keyword_dropdown_selector.html")
    return t.render(Context({
        'keyword_groups': Keyword.get_groups(),
        'input_selector': input_selector,
        'identify': get_random_string(6),
        'small': True }))