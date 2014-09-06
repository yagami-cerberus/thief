
from django import template
from django.template import Context
from django.template.loader import get_template
from django import forms
from django.utils.html import mark_safe

register = template.Library()

def order_icon(asc):
    if asc:
        return '<span class="glyphicon glyphicon-chevron-up"></span>'
    else:
        return '<span class="glyphicon glyphicon-chevron-down"></span>'

class OrderHeaderNode(template.Node):
    def __init__(self, nodes, field_name):
        self.nodes = nodes
        self.field_name = field_name
    
    def current_index(self, context):
        try:
            return abs(int(context['o']))
        except ValueError:
            return 0
    
    def selected_index(self, context):
        return context['order_reference'].index(self.field_name)
    
    def is_desc(self, context):
        return context['o'].startswith("-")
    
    def render(self, context):
        current_index = self.current_index(context)
        selected_index = self.selected_index(context)
        is_desc = self.is_desc(context)
        
        qs = context['request'].GET.copy()
        
        if current_index == selected_index:
            if is_desc:
                qs['o'] = '%s' % selected_index
                context['icon'] = mark_safe(order_icon(asc=False))
            else:
                qs['o'] = '-%s' % selected_index
                context['icon'] = mark_safe(order_icon(asc=True))
        else:
            qs['o'] = '%s' % selected_index
            context['icon'] = mark_safe('')

        context['url'] = qs.urlencode()
        return self.nodes.render(context)
    
@register.tag
def orderheader(parser, token):
    nodelist = parser.parse(('endorderheader',))
    parser.delete_first_token()
    return OrderHeaderNode(nodelist, token.contents.split(' ')[-1])
