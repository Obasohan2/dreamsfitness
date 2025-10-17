from decimal import Decimal
from .cart import Cart

def cart_contents(request):
    """
    Make cart data available in all templates.
    """
    cart = Cart(request)
    cart_items = list(cart)
    total_price = cart.get_total_price()
    cart_count = len(cart)

    delivery = Decimal('0.00')
    grand_total = total_price + delivery

    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'total_price': total_price,
        'delivery': delivery,
        'grand_total': grand_total,
    }
    return context
