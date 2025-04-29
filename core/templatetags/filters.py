from django import template

register = template.Library()


@register.filter
def endswith(value, arg):
    """Returns True if the value ends with the argument."""
    return str(value).endswith(arg)
