import requests
from constance import config
from django.db.models import Manager

from evibes.settings import logger


class TransactionManager(Manager):

    def process_transaction(self, transaction):
        payment_request = requests.post(config.PAYMENT_GATEWAY_URL, json={
            "order_id": str(transaction.uuid),
            "email": transaction.balance.user.email,
            "amount": transaction.amount,
            "currency": "EUR",
            "return_url": f"https://{config.FRONTEND_DOMAIN}/",
            "callback_url": f"https://api.{config.BASE_DOMAIN}/payments/{transaction.uuid}/callback/",
            "wallet_acception_type": "ask_on_purchase",
            "locale": transaction.balance.user.language.split('-')[0],
            "allow_change_currency": True,
        }, headers={'Content-Type': 'application/json',
                    'Authorization': f'Token token={config.PAYMENT_GATEWAY_TOKEN}'})
        if payment_request.status_code == 200:
            transaction.process['redirect_url'] = payment_request.json().get('url', 'http://404.org')
            transaction.save()
        else:
            logger.error(payment_request.text)
        return transaction

    def create(self, **kwargs):
        transaction = super().create(**kwargs)
        if transaction.order:
            transaction.amount += 5
            transaction.save()
        return self.process_transaction(
            transaction
        )
