from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse 
from products.models import Product
from .models import Cart, CartItem, Subscription


# -----------------------------
# Helper
# -----------------------------
def get_user_cart(request):
    """Get or create a cart for the current user or guest (session-based)."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        # Guest user (no account)
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id, user=None).first()
            if not cart:
                cart = Cart.objects.create()  # new guest cart
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart


# -----------------------------
# Cart Page
# -----------------------------
def cart_view(request):
    cart = get_user_cart(request)
    total_price = cart.total_price()
    cart_count = cart.total_items()

    context = {
        'cart_items': cart.items.all(),
        'subscription': cart.subscription,
        'total_price': total_price,
        'cart_count': cart_count,
    }
    return render(request, 'cart/cart.html', context)


# -----------------------------
# Add Product (guests allowed)
# -----------------------------
from django.urls import reverse

@require_POST
def add_to_cart(request, product_id):
    """Add a product to the user's or guest's cart, handle Buy Now redirects."""
    cart = get_user_cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1

    # Add or update cart item
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = item.quantity + quantity if not created else quantity
    item.price = product.price
    item.save()

    # Handle "Buy Now" logic
    if request.POST.get("buy_now"):
        if request.user.is_authenticated:
            return redirect('checkout')
        else:
            login_url = reverse('account_login')
            next_url = reverse('checkout')
            return redirect(f"{login_url}?next={next_url}")

    # Normal add to cart
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart:cart_view')

# -----------------------------
# Update Quantity
# -----------------------------
@require_POST
def update_cart(request, product_id):
    """Update item quantity (guest or logged-in)."""
    cart = get_user_cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = quantity
    item.save()
    messages.success(request, f"Updated quantity for {product.name}.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.total_price()),
            'cart_count': cart.total_items(),
        })

    return redirect('cart:cart_view')


# -----------------------------
# Remove Product
# -----------------------------
def remove_from_cart(request, product_id):
    cart = get_user_cart(request)
    item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if item:
        item.delete()
        messages.success(request, "Item removed from your cart.")
    return redirect('cart:cart_view')


# -----------------------------
# Clear Entire Cart
# -----------------------------
def clear_cart(request):
    cart = get_user_cart(request)
    cart.items.all().delete()
    cart.subscription = None
    cart.save()
    messages.info(request, "Your cart has been cleared.")
    return redirect('cart:cart_view')


# -----------------------------
# Add Subscription (login required)
# -----------------------------
@login_required
def add_subscription_to_cart(request, subscription_id):
    cart = get_user_cart(request)
    subscription = get_object_or_404(Subscription, id=subscription_id, active=True)

    if cart.subscription and cart.subscription.id == subscription.id:
        messages.info(request, f"You already have {subscription.title} in your cart.")
    else:
        cart.subscription = subscription
        cart.save()
        messages.success(request, f"{subscription.title} added to your cart.")

    return redirect('cart:cart_view')


# -----------------------------
# Remove Subscription
# -----------------------------
@login_required
def remove_subscription_from_cart(request):
    cart = get_user_cart(request)
    if cart.subscription:
        messages.info(request, f"{cart.subscription.title} removed from your cart.")
        cart.subscription = None
        cart.save()
    return redirect('cart:cart_view')


# -----------------------------
# Checkout Page
# -----------------------------
@login_required
def checkout(request):
    cart = get_user_cart(request)
    if cart.items.count() == 0 and not cart.subscription:
        messages.warning(request, "Your cart is empty.")
        return redirect('products:all_products')

    context = {
        'cart_items': cart.items.all(),
        'subscription': cart.subscription,
        'total_price': cart.total_price(),
    }
    return render(request, 'checkout/checkout.html', context)
