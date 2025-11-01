from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def restore_cart_after_login(sender, request, user, **kwargs):
    """
    Restore guest cart into the user's session after login.
    Works for normal logins and social logins (e.g., allauth).
    """
    pre_login_cart = request.session.pop('pre_login_cart', None)
    if pre_login_cart:
        if 'cart' not in request.session:
            # No existing cart after login
            request.session['cart'] = pre_login_cart
        else:
            # Merge both carts (if any)
            for pid, item in pre_login_cart.items():
                if pid in request.session['cart']:
                    request.session['cart'][pid]['quantity'] += item['quantity']
                else:
                    request.session['cart'][pid] = item

        request.session.modified = True
