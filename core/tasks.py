import os
import random
import shutil
import uuid
from datetime import date, timedelta
from time import sleep

import requests
from celery.app import shared_task
from celery.utils.log import get_task_logger
from constance import config
from django.core.cache import cache

from core.models import Product, ProductTag, Promotion
from core.utils.caching import set_default_cache
from core.vendors import delete_stale
from evibes.settings import MEDIA_ROOT

logger = get_task_logger(__name__)


@shared_task
def update_products_task():
    """
    Run a background task to update product data and manage stale products.

    This function checks if the update task is already running using a cache-based
    flag. If the task is not running, it initiates the update process, which
    includes invoking the `update_stock` method of vendor classes and removing
    stale products. Finally, it clears the flag in the cache.

    Just write integrations with your vendors' APIs into core/vendors/<vendor_name>.py and use it here :)

    :return: A tuple consisting of a status boolean and a message string
    :rtype: tuple[bool, str]
    """
    update_products_task_running = cache.get("update_products_task_running", False)

    if not update_products_task_running:
        cache.set("update_products_task_running", True, 86400)
        vendors_classes = []

        for vendor_class in vendors_classes:
            vendor = vendor_class()
            vendor.update_stock()

        delete_stale()

        cache.delete("update_products_task_running")

    return True, "Success"


@shared_task
def update_orderproducts_task():
    """
    Updates the statuses of order products for all vendors listed in the
    `vendors_classes`. Each vendor class in the `vendors_classes` list is
    instantiated, and the `update_order_products_statuses` method of the
    respective vendor instance is executed to handle the update process.
    Just write integrations with your vendors' APIs into core/vendors/<vendor_name>.py and use it here :)

    :return: A tuple containing a boolean indicating success and a string
        message confirming the successful execution of the task.
    :rtype: Tuple[bool, str]
    """
    vendors_classes = []

    for vendor_class in vendors_classes:
        vendor = vendor_class()
        vendor.update_order_products_statuses()

    return True, "Success"


@shared_task
def set_default_caches_task():
    """
    Task to set default caches in the application's memory.

    This task is designed to configure and set up default caches that are used
    within the application framework.

    :return: A tuple containing a boolean indicating success and a message
    :rtype: tuple[bool, str]
    """
    set_default_cache()

    return True, "Success"


@shared_task
def remove_stale_product_images():
    """
    Removes stale product images from the products directory by identifying directories
    whose names do not match any UUIDs currently present in the database.

    The task scans the product images directory to locate subdirectories named after
    product UUIDs. It verifies whether each UUID is part of the database's current
    product records. If a directory's UUID is not found in the database, it deletes
    the directory, as it is considered stale. This helps in maintaining a clean storage
    and removing unused image data.

    :raises ValueError: If a directory name is not a valid UUID.
    :raises Exception: If an error occurs while attempting to delete a stale directory.

    :return: None
    """
    products_dir = os.path.join(MEDIA_ROOT, "products")
    if not os.path.isdir(products_dir):
        logger.info("The products directory does not exist: %s", products_dir)
        return

    # Load all current product UUIDs into a set.
    # This query returns all product UUIDs (as strings or UUID objects).
    current_product_uuids = set(Product.objects.values_list("uuid", flat=True))
    logger.info("Loaded %d product UUIDs from the database.", len(current_product_uuids))

    # Iterate through all subdirectories in the products folder.
    for entry in os.listdir(products_dir):
        entry_path = os.path.join(products_dir, entry)
        if os.path.isdir(entry_path):
            try:
                # Validate that the directory name is a proper UUID.
                product_uuid = uuid.UUID(entry)
            except ValueError:
                logger.debug("Skipping directory with non-UUID name: %s", entry)
                continue

            # Check if the UUID is in the set of current product UUIDs.
            if product_uuid not in current_product_uuids:
                try:
                    shutil.rmtree(entry_path)
                    logger.info("Removed stale product images directory: %s", entry_path)
                except Exception as e:
                    logger.error("Error removing directory %s: %s", entry_path, e)


@shared_task
def process_promotions() -> tuple[bool, str]:
    """
    Processes and updates promotions based on holiday data or default settings.

    This task fetches holiday information for the next four days from the Abstract API.
    If a matching holiday is found, it creates a promotion associated with the holiday
    name. If no holiday is detected, it creates a default "Special Offers" promotion.
    A random discount percentage is applied to the selected products.

    Promotions are created only if there are at least 48 eligible products.
    All existing promotions are deleted before creating new ones.

    :raises HTTPError: If the API request to the Abstract API fails with an HTTP error.
    :raises Exception: If any general error occurs during API communication or data processing.

    :return: A tuple where the first element is a boolean indicating success, and the second
        element is a message describing the operation's outcome.
    :rtype: tuple[bool, str]
    """
    if not config.ABSTRACT_API_KEY or config.ABSTRACT_API_KEY == "example key":
        return False, "Abstract features disabled."

    Promotion.objects.all().update(is_active=False)

    holiday_data = None

    for day_offset in range(4):
        checked_date = date.today() + timedelta(days=day_offset)
        response = requests.get(
            f"https://holidays.abstractapi.com/v1/?api_key={config.ABSTRACT_API_KEY}&country=GB&"
            f"month={checked_date.month}&day={checked_date.day}"
        )
        response.raise_for_status()
        holidays = response.json()
        if holidays:
            holiday_data = holidays[0]
            break
        sleep(1)

    if holiday_data:
        holiday_name = holiday_data["name"]
        promotion_name = f"{holiday_name} Sale"
        discount_percent = random.randint(10, 15)

    else:
        promotion_name = "Special Offers"
        discount_percent = random.randint(10, 15)

    eligible_products = Product.objects.filter(
        is_active=True,
        stocks__price__gt=0,
    )

    if eligible_products.count() < 48:
        return False, "Not enough products to choose from [< 48]."

    selected_products = []

    while len(selected_products) < 48:
        product = eligible_products.order_by("?").first()
        selected_products.append(product)

    promotion = Promotion.objects.create(name=promotion_name, discount_percent=discount_percent, is_active=True)

    promotion.products.set(selected_products)

    return True, "Promotions updated successfully."
