import json
from contextlib import suppress
from math import ceil

from django.db import IntegrityError

from core.elasticsearch import process_query
from core.models import Attribute, AttributeGroup, AttributeValue, Brand, Category, Product, Stock, Vendor
from payments.errors import RatesError
from payments.utils import get_rates


class AbstractVendor:
    """
    Abstract class defining vendor-related operations and handling.

    This class provides methods to manage and manipulate data related to a vendor
    and its associated products, stocks, and attributes. These include utility
    methods for chunking data, resolving prices based on vendor or category
    specific markup percentages, retrieving vendor instances, fetching queryset
    data for products and stocks, and performing bulk operations like updates or
    deletions on inactive objects.

    Attributes:
        vendor_name (str | None): Name of the vendor associated with this class
        instance.
    """

    def __init__(self, vendor_name=None, currency="USD"):
        self.vendor_name = vendor_name
        self.currency = currency
        self.blocked_attributes = []

    @staticmethod
    def chunk_data(data, num_chunks=20):
        total = len(data)
        if total == 0:
            return []
        chunk_size = max(1, (total + num_chunks - 1) // num_chunks)
        return [data[i: i + chunk_size] for i in range(0, total, chunk_size)]

    @staticmethod
    def auto_convert_value(value):
        """
        Attempts to convert a value to a more specific type.
        Handles booleans, numbers, objects (dicts), and arrays (lists),
        even when they are provided as strings.
        Returns a tuple of (converted_value, type_label).
        """
        # First, handle native types
        if isinstance(value, bool):
            return value, "boolean"
        if isinstance(value, int):
            return value, "integer"
        if isinstance(value, float):
            return value, "float"
        if isinstance(value, dict):
            # Convert dict to a JSON string for consistency in storage
            return json.dumps(value), "object"
        if isinstance(value, list):
            # Similarly, convert list to JSON string
            return json.dumps(value), "array"

        # Now, if it's a string, try to parse it further
        if isinstance(value, str):
            lower_val = value.lower().strip()
            # Handle booleans in string form.
            if lower_val == "true":
                return True, "boolean"
            if lower_val == "false":
                return False, "boolean"

            # Try integer conversion.
            with suppress(ValueError):
                int_val = int(value)
                # Check that converting back to string gives the same value (avoid "100.0" issues).
                if str(int_val) == value:
                    return int_val, "integer"

            # Try float conversion.
            with suppress(ValueError):
                float_val = float(value)
                return float_val, "float"

            # Try to detect a JSON object or array.
            stripped_value = value.strip()
            if (stripped_value.startswith("{") and stripped_value.endswith("}")) or (
                    stripped_value.startswith("[") and stripped_value.endswith("]")
            ):
                with suppress(Exception):
                    parsed = json.loads(value)
                    if isinstance(parsed, dict):
                        # Store as JSON string for consistency.
                        return json.dumps(parsed), "object"
                    elif isinstance(parsed, list):
                        return json.dumps(parsed), "array"

        # Default case: treat as a plain string.
        return value, "string"

    @staticmethod
    def auto_resolver_helper(model: type[Brand] | type[Category], resolving_name: str):
        queryset = model.objects.filter(name=resolving_name)
        if not queryset.exists():
            return model.objects.get_or_create(name=resolving_name, defaults={"is_active": False})
        elif queryset.filter(is_active=True).count() > 1:
            queryset = queryset.filter(is_active=True)
        elif queryset.filter(is_active=False).count() > 1:
            queryset = queryset.filter(is_active=False)
        chosen = queryset.first()
        queryset = queryset.exclude(uuid=chosen.uuid)
        queryset.delete()
        return chosen

    def auto_resolve_category(self, category_name: str):
        if category_name:
            try:
                uuid = process_query(category_name)["categories"][0]["uuid"]
                if uuid:
                    return Category.objects.get(uuid=uuid)
            except KeyError:
                pass
            except IndexError:
                pass
            except Category.MultipleObjectsReturned:
                pass
            except Category.DoesNotExist:
                pass

        return self.auto_resolver_helper(Category, category_name)

    def auto_resolve_brand(self, brand_name: str):
        if brand_name:
            try:
                uuid = process_query(brand_name)["brands"][0]["uuid"]
                if uuid:
                    return Brand.objects.get(uuid=uuid)
            except KeyError:
                pass
            except IndexError:
                pass
            except Brand.MultipleObjectsReturned:
                pass
            except Brand.DoesNotExist:
                pass

        return self.auto_resolver_helper(Brand, brand_name)

    def resolve_price(self, original_price: int | float, vendor: Vendor = None, category: Category = None) -> float:
        if not vendor:
            vendor = self.get_vendor_instance()

        if not category and not vendor:
            raise ValueError("Either category or vendor must be provided.")

        price = float(original_price)

        if category and category.markup_percent:
            price *= 1 + category.markup_percent / 100.0
        elif vendor and vendor.markup_percent:
            price *= 1 + vendor.markup_percent / 100.0

        return round(price, 2)

    def resolve_price_with_currency(self, price, provider):
        rates = get_rates(provider)

        rate = rates.get(self.currency)

        if not rate:
            raise RatesError(f"No rate found for {self.currency} in {rates} with probider {provider}...")

        return round(price / rate, 2) if rate else round(price, 2)

    @staticmethod
    def round_price_marketologically(price: float) -> float:
        up_int = ceil(price)
        s = str(up_int)
        s = (s[:-1] if len(s) > 1 else '0') + '9'
        return float(f"{int(s):.2f}")

    def get_vendor_instance(self):
        try:
            vendor = Vendor.objects.get(name=self.vendor_name)
            if vendor.is_active:
                return vendor
            raise VendorError(f"Vendor {self.vendor_name!r} is inactive...")
        except Vendor.DoesNotExist:
            raise Exception(f"No matching vendor found with name {self.vendor_name!r}...")

    def get_products(self):
        pass

    def get_products_queryset(self):
        return Product.objects.filter(stocks__vendor=self.get_vendor_instance(), orderproduct__isnull=True)

    def get_stocks_queryset(self):
        return Stock.objects.filter(product__in=self.get_products_queryset(), product__orderproduct__isnull=True)

    def get_attribute_values_queryset(self):
        return AttributeValue.objects.filter(
            product__in=self.get_products_queryset(), product__orderproduct__isnull=True
        )

    def prepare_for_stock_update(self):
        self.get_products_queryset().update(is_active=False)

    def delete_inactives(self):
        self.get_products_queryset().filter(is_active=False).delete()

    def delete_belongings(self):
        self.get_products_queryset().delete()
        self.get_stocks_queryset().delete()
        self.get_attribute_values_queryset().delete()

    def process_attribute(self, key: str, value, product: Product, attr_group: AttributeGroup):

        if not value:
            return

        if not attr_group:
            return

        if key in self.blocked_attributes:
            return

        value, attr_value_type = self.auto_convert_value(value)

        is_created = False

        try:
            attribute, is_created = Attribute.objects.get_or_create(
                name=key,
                group=attr_group,
                value_type=attr_value_type,
                defaults={"is_active": True},
            )
        except Attribute.MultipleObjectsReturned:
            attribute = Attribute.objects.filter(name=key, group=attr_group).order_by("uuid").first()
            attribute.is_active = True
            attribute.value_type = attr_value_type
            attribute.save()
        except IntegrityError:
            return

        attribute.categories.add(product.category)
        attribute.save()

        if not is_created:
            return

        AttributeValue.objects.get_or_create(
            attribute=attribute,
            value=value,
            product=product,
            defaults={"is_active": True},
        )

    def update_stock(self):
        pass

    def update_order_products_statuses(self):
        pass


def delete_stale():
    Product.objects.filter(stocks__isnull=True, orderproduct__isnull=True).delete()


class NotEnoughBalanceError(Exception):
    """
    Custom exception raised when a financial operation exceeds
    the available balance.

    This exception is designed to enforce balance constraints on
    operations such as withdrawals or payments, ensuring that
    transactions do not cause the balance to go below the allowed
    limit.
    """

    pass


class WrongUserAttributesError(Exception):
    """
    Exception class representing an error for incorrect user attributes.

    This exception is raised when invalid or inconsistent attributes
    are provided for a user during an operation. It can be used to
    signal issues related to user data validation or parameter checks.
    """

    pass


class VendorError(Exception):
    """
    Exception class representing an error for vendor-related operations.

    This exception is raised when unexpected output is received from Vendor API.
    """

    pass
