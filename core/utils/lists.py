FAILED_STATUSES = ["FAILED", "CANCELED", "RETURNED"]

PRODUCTS_ORDERING_FIELDS = ["name", "price", "quantity"]

TRANSACTION_SUCCESSFUL_STATUSES = [
    "purchase_complete",
    "successful",
]

TRANSACTION_FAILED_STATUSES = [
    "failed",
    "canceled",
]

BAD_KEYS_TO_LISTEN = [
    "is_staff",
    "is_superuser",
    "is_active",
    "active",
]
