import random
from .models import Order

def generate_unique_order_number():
    while True:
        number = str(random.randint(100000, 999999))
        if not Order.objects.filter(order_number=number).exists():
            return number