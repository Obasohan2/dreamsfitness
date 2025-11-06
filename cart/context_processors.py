from .models import Cart


def cart_context(request):
    """Makes cart data available globally — for both users and guests."""
    cart_count = 0
    grand_total = 0

    # Only fetch cart if session or user exists
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id, user=None).first() if cart_id else None

    if cart:
        cart_count = cart.total_items()
        grand_total = cart.total_price()

    return {
        'cart_count': cart_count,
        'grand_total': grand_total,
    }
