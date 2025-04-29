from django.core.exceptions import BadRequest


class NotEnoughMoneyError(BadRequest):
    pass
