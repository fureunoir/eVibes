from django.core.exceptions import BadRequest, ImproperlyConfigured


class NotEnoughMoneyError(BadRequest):
    pass


class DisabledCommerceError(ImproperlyConfigured):
    pass
