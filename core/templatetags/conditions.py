from django import template

register = template.Library()


@register.filter
def attributes_length(value, arg):
    """Returns True if the value length is more than the argument."""
    return len(value) > arg
