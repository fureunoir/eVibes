# payments/tests/test_payments.py


import graphene
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from graphene.test import Client as GrapheneClient
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from payments.graphene.mutations import Deposit  # the GraphQL Deposit mutation
from payments.models import Balance, Transaction
from payments.views import CallbackAPIView, DepositView

###############################################################################
# Model Tests
###############################################################################


class BalanceModelTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        # Create a user – the post-save signal will auto-create a Balance.
        self.user = self.user_model.objects.create_user(email="test@example.com", password="pass")
        self.balance = Balance.objects.get(user=self.user)

    def test_balance_rounding(self):
        """
        If the balance amount has more than two decimal places,
        the save() method should round it to 2 decimals.
        """
        self.balance.amount = 10.129
        self.balance.save()
        self.balance.refresh_from_db()
        # round(10.129, 2) == 10.13
        self.assertAlmostEqual(self.balance.amount, 10.13, places=2)


class TransactionModelTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(email="trans_test@example.com", password="pass")
        self.balance = Balance.objects.get(user=self.user)

    def test_transaction_rounding(self):
        """
        When a Transaction is saved with an amount having more than two decimals,
        it should be rounded to 2 decimal places.
        """
        t = Transaction(balance=self.balance, amount=5.6789, currency="EUR", payment_method="card")
        t.save()
        self.assertAlmostEqual(t.amount, 5.68, places=2)

    def test_transaction_zero_amount_raises(self):
        """
        Saving a Transaction with a 0 amount should raise a ValueError.
        """
        with self.assertRaises(ValueError):
            t = Transaction(balance=self.balance, amount=0.0, currency="EUR", payment_method="card")
            t.save()


###############################################################################
# API (View) Tests
###############################################################################


class DepositViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(email="deposit@example.com", password="pass")
        self.deposit_view = DepositView.as_view()

    def test_deposit_view_unauthenticated(self):
        """
        An unauthenticated user should receive a 401 Unauthorized response.
        """
        request = self.factory.post("/deposit/", {"amount": 100.0})
        # Do not attach a user to the request.
        response = self.deposit_view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deposit_view_authenticated(self):
        """
        An authenticated user posting a deposit should get a 201 Created response
        and a transaction with processing details.
        """
        request = self.factory.post("/deposit/", {"amount": 100.0})
        force_authenticate(request, user=self.user)
        response = self.deposit_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # The response should include the 'process' field.
        self.assertIn("process", response.data)


class CallbackViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.callback_view = CallbackAPIView.as_view()

    def test_callback_view_unknown_gateway(self):
        """
        If an unknown gateway is specified, the callback should return a 500 error.
        """
        data = {"sample": "data"}
        request = self.factory.post("/callback/?gateway=unknown", data, format="json")
        response = self.callback_view(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


###############################################################################
# Signal Tests
###############################################################################


class SignalTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_create_balance_on_user_creation(self):
        """
        When a new User is created, the post_save signal should create an associated Balance.
        """
        user = self.user_model.objects.create_user(email="signal@example.com", password="pass")
        balance = Balance.objects.get(user=user)
        self.assertIsNotNone(balance)


###############################################################################
# GraphQL Tests
###############################################################################


class GraphQLDepositTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(email="graphql@example.com", password="pass")
        # Ensure a Balance exists via the signal.
        self.balance = Balance.objects.get(user=self.user)

        # Create a minimal schema including the Deposit mutation.
        class Mutation(graphene.ObjectType):
            deposit = Deposit.Field()

        self.schema = graphene.Schema(mutation=Mutation)
        self.client = GrapheneClient(self.schema)

    def test_graphql_deposit_authenticated(self):
        """
        An authenticated GraphQL deposit mutation should create a Transaction.
        """
        mutation = """
            mutation Deposit($amount: Float!) {
                deposit(amount: $amount) {
                    transaction {
                        id
                        amount
                    }
                }
            }
        """
        result = self.client.execute(mutation, variable_values={"amount": 100.0}, context_value={"user": self.user})
        # There should be no errors.
        self.assertNotIn("errors", result)
        transaction_data = result.get("data", {}).get("deposit", {}).get("transaction")
        self.assertIsNotNone(transaction_data)
        self.assertAlmostEqual(float(transaction_data["amount"]), 100.0, places=2)

    def test_graphql_deposit_unauthenticated(self):
        """
        An unauthenticated GraphQL deposit mutation should raise a permission error.
        """
        mutation = """
            mutation Deposit($amount: Float!) {
                deposit(amount: $amount) {
                    transaction {
                        id
                        amount
                    }
                }
            }
        """
        result = self.client.execute(
            mutation, variable_values={"amount": 100.0}, context_value={"user": AnonymousUser()}
        )
        self.assertIn("errors", result)
        error_message = result["errors"][0]["message"]
        self.assertIn("permission", error_message.lower())
