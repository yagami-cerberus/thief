from django.utils.crypto import get_random_string
from django.template.loader import get_template
from django.template import Context
from django import template

from thief.auction.models import Catalog, Keyword, KeywordSet
from thief.auction.forms import CatalogWidget

register = template.Library()

@register.simple_tag(name='load_keyword_groups', takes_context=True)
def load_keyword_groups(context):
    context['keyword_groups'] = Catalog.objects.values_list("name", flat=True)
    return ""

@register.simple_tag(name='catalog_selector')
def catalog_selector(name, value, css=""):
    queryset = Catalog.objects.order_by("name").values_list("id", "name")
    return CatalogWidget({}, queryset).render(name, value, {"class": css})
