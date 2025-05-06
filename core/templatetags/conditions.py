from django import template

register = template.Library()


@register.filter
def attributes_length(value, arg):
    """Returns True if the value length is more than the argument."""
    if isinstance(value, dict):
        count = int()
        for attribute, _value in value.items():
            if attribute.endswith("_system"):
                continue
            count += 1
        return count > arg
    return False
