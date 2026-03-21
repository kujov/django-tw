from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from django_wind.conf import get_config

register = template.Library()


@register.simple_tag
def wind_css():
    config = get_config()
    url = static(config.output_css)
    return mark_safe(f'<link rel="stylesheet" href="{url}">')
