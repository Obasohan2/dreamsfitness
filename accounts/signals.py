from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver
from cart.models import Cart
from .models import Profile


# --- Create and Save Profile Automatically ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


# --- Merge Guest Cart into User Cart on Login ---
@receiver(user_logged_in)
def merge_guest_cart(sender, user, request, **kwargs):
    """
    When a user logs in, merge any guest cart stored in session
    into the user's persistent cart.
    """
    cart_id = request.session.get('cart_id')
    if cart_id:
        guest_cart = Cart.objects.filter(id=cart_id, user=None).first()
        if guest_cart:
            user_cart, _ = Cart.objects.get_or_create(user=user)
            for item in guest_cart.items.all():
                existing_item = user_cart.items.filter(product=item.product).first()
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                else:
                    item.cart = user_cart
                    item.save()

            # Delete the guest cart and clear session reference
            guest_cart.delete()
            del request.session['cart_id']
