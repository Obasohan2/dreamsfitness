from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.conf import settings
import stripe

from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount
from cart.cart import Cart

# stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout_preview(request):
    """
    Display checkout summary for selected plan and/or products in cart.
    """
    plan_id = request.GET.get('plan_id') or request.GET.get('plan')
    plan = None
    plan_price = Decimal('0.00')
    cart_total = Decimal('0.00')
    total_price = Decimal('0.00')
    balance_seats = 0
    is_full = False

    # Load selected plan (if any)
    if plan_id:
        plan = get_object_or_404(SubPlan, id=plan_id)
        plan_price = Decimal(plan.price)
        balance_seats = max(plan.max_member - plan.total_members, 0)
        is_full = balance_seats <= 0

    # Load cart (session-based)
    cart = Cart(request)
    cart_total = Decimal(cart.get_total_price()) if len(cart) > 0 else Decimal('0.00')

    total_price = plan_price + cart_total

    if not plan and len(cart) == 0:
        return render(request, 'checkout/empty_checkout.html')

    context = {
        "plan": plan,
        "cart": cart,
        "balance_seats": balance_seats,
        "is_full": is_full,
        "total_price": total_price,
    }
    return render(request, "checkout/checkout_preview.html", context)


@require_POST
@login_required
def checkout_session(request):
    """
    Validates the checkout, applies discounts, and creates a Stripe session (or simulated success).
    """
    cart = Cart(request)
    plan_id = request.POST.get("plan_id")
    validity_months = request.POST.get("validity")
    plan = None
    total_amount = Decimal('0.00')
    discount_percent = Decimal('0.00')

    # --- Retrieve plan and discount ---
    if plan_id:
        plan = get_object_or_404(SubPlan, id=plan_id)
        plan_price = Decimal(plan.price)
        months = int(validity_months or 1)

        discount_obj = PlanDiscount.objects.filter(plan=plan, total_months=months).first()
        if discount_obj:
            discount_percent = Decimal(discount_obj.total_discount)

        subtotal = plan_price * months
        discounted_amount = subtotal - (subtotal * discount_percent / 100)
        total_amount += discounted_amount

    # --- Add cart total ---
    cart_total = Decimal(cart.get_total_price()) if len(cart) > 0 else Decimal('0.00')
    total_amount += cart_total

    # --- Seat availability check ---
    if plan and plan.max_member <= plan.total_members:
        messages.error(request, "Sorry, this plan is now full.")
        return redirect("checkout_preview")

    # --- Final total safeguard ---
    if total_amount <= 0:
        messages.error(request, "Your total amount is invalid.")
        return redirect("checkout_preview")

    # --- (Optional) Stripe checkout logic ---
    # line_items = []
    # if plan:
    #     line_items.append({
    #         'price_data': {
    #             'currency': 'gbp',
    #             'product_data': {'name': f'Subscription - {plan.title}'},
    #             'unit_amount': int(discounted_amount * 100),
    #         },
    #         'quantity': 1,
    #     })
    # for item in cart:
    #     line_items.append({
    #         'price_data': {
    #             'currency': 'gbp',
    #             'product_data': {'name': item['product'].name},
    #             'unit_amount': int(item['product'].price * 100),
    #         },
    #         'quantity': item['quantity'],
    #     })
    #
    # session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     line_items=line_items,
    #     mode='payment',
    #     success_url=request.build_absolute_uri('/checkout/success/'),
    #     cancel_url=request.build_absolute_uri('/checkout/cancel/'),
    # )
    #
    # return redirect(session.url, code=303)

    # --- Simulated success (no Stripe yet) ---
    messages.success(request, f"Checkout initiated successfully. Total: £{total_amount:.2f}")
    return redirect("checkout_success")


@login_required
def checkout_success(request):
    """
    After successful checkout:
    - Activate subscription (if purchased)
    - Clear cart
    - Show success page
    """
    cart = Cart(request)
    cart.clear()
    return render(request, 'checkout/success.html')


@login_required
def checkout_cancel(request):
    """Handles user cancellation of payment."""
    return render(request, 'checkout/cancel.html')
