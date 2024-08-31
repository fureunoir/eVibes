import random

from app.models import Product


def set_random_ratings():
    products = Product.objects.all()
    for product in products:
        if random.random() < 0.7:
            product.rating = round(random.uniform(5, 10))
        else:
            product.rating = round(random.uniform(1, 5))
        product.save()

    return True, "Random ratings were set"
