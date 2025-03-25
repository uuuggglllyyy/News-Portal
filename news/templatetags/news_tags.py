from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def truncatewords(value, arg):
    """
    Truncates a string after a certain number of words, including
    only full words.
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int().
        return value  # Fail silently.

    words = value.split()
    if len(words) > length:
        return ' '.join(words[:length]) + '...'
    return value