import random
from datetime import date, timedelta
from time import sleep

import requests
from constance import config
from django.db.models import Q, Avg

from core.models import Product, Promotion


def work_promotions() -> tuple[bool, str]:
    Promotion.objects.all().delete()

    holiday_data = None

    for day_offset in range(4):
        checked_date = date.today() + timedelta(days=day_offset)
        response = requests.get(
            f'https://holidays.abstractapi.com/v1/?api_key={config.ABSTRACT_API_KEY}&country=DE&'
            f'month={checked_date.month}&day={checked_date.day}')
        response.raise_for_status()
        holidays = response.json()
        if holidays:
            holiday_data = holidays[0]
            break
        sleep(1)

    if holiday_data:
        holiday_name = holiday_data['name']
        promotion_name = f"{holiday_name} Sale"
        discount_percent = random.randint(10, 15)

    else:
        promotion_name = f"Special Offers"
        discount_percent = random.randint(10, 15)

    eligible_products = Product.objects.annotate(
        average_rating=Avg('feedbacks__rating', filter=Q(feedbacks__active=True))
    ).filter(average_rating__gte=7).order_by('-average_rating')

    if eligible_products.count() < 48:
        return False, "Not enough products to choose from [< 48]."

    selected_products = random.sample(list(eligible_products), 48)

    promotion = Promotion.objects.create(
        name=promotion_name,
        discount_percent=discount_percent,
        is_active=True
    )

    promotion.products.set(selected_products)

    return True, "Promotions updated successfully."
