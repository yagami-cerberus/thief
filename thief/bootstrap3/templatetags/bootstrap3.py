
import hashlib

from django import template
from django.template import Context
from django.template.loader import get_template
from django import forms

register = template.Library()

@register.filter
def bootstrap_field(field):
    if isinstance(field.field.widget, (forms.CheckboxInput, forms.RadioSelect)):
        return field.as_widget(attrs={})
    elif isinstance(field.field.widget, (forms.TextInput, )):
        return field.as_widget(attrs={"class": "form-control", "placeholder": field.help_text})
    else:
        return field.as_widget(attrs={"class": "form-control"})


@register.filter
def bootstrap_form(form, layout="default"):
    options = layout.split(",")

    if options[0] == "default":
        return get_template("bootstrap3/form.html").render(
            Context({
                'form': form
            })
        )
    elif options[0] == "h":
        label_col = int(options[1])
        input_col = 12 - label_col
        return get_template("bootstrap3/form-horizontal.html").render(
            Context({
                'form': form,
                'label_col': label_col,
                'input_col': input_col
            })
        )
