from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe

from products.models import Product
from subscriptions.models import SubPlan
from cart.cart import Cart

# stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
@login_required
def checkout(request):
    cart = Cart(request)
    plan_id = request.GET.get('plan')
    plan = None

    if plan_id:
        plan = get_object_or_404(SubPlan, id=plan_id)

    cart_total = cart.get_total_price() if len(cart) > 0 else 0
    plan_total = plan.price if plan else 0
    total_price = cart_total + plan_total

    if not plan and len(cart) == 0:
        return render(request, 'checkout/empty_checkout.html')

    context = {
        'plan': plan,
        'cart': cart,
        'total_price': total_price,
    }
    return render(request, 'checkout/checkout.html', context)


@login_required
def checkout_session(request):
    """
    Temporary test version — bypasses Stripe and simulates a successful payment.
    """
    cart = Cart(request)
    plan_id = request.POST.get('plan_id')
    plan = None

    if plan_id:
        plan = get_object_or_404(SubPlan, id=plan_id)

    # Just build the context so you can test logic and totals
    line_items = []

    if plan:
        line_items.append({
            'name': f"Subscription - {plan.title}",
            'price': plan.price,
            'quantity': 1,
        })

    for item in cart:
        product = item['product']
        line_items.append({
            'name': product.name,
            'price': product.price,
            'quantity': item['quantity'],
        })

    #  Log or print to confirm it's working
    print("Simulated checkout line items:", line_items)

    #  Instead of creating a Stripe session, just redirect to success
    return redirect('checkout_success')


@login_required
def checkout_success(request):
    # You can add logic here:
    # - mark the subscription active
    # - clear cart
    # - send email confirmation
    cart = Cart(request)
    cart.clear()
    return render(request, 'checkout/success.html')


@login_required
def checkout_cancel(request):
    return render(request, 'checkout/cancel.html')
