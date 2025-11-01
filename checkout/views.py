from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from decimal import Decimal

from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount
from cart.cart import Cart
from .models import Order, OrderItem


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


@login_required
@require_POST
def checkout_session(request):
    """
    Process checkout locally (no Stripe). Creates order + items, clears cart, and redirects.
    """
    cart = Cart(request)
    plan_id = request.POST.get("plan_id")
    validity_months = request.POST.get("validity")

    plan = None
    total_amount = Decimal("0.00")

    # --- Handle Plan ---
    if plan_id:
        plan = get_object_or_404(SubPlan, id=plan_id)
        months = int(validity_months or 1)
        plan_price = Decimal(plan.price)

        # use 'subplan' instead of 'plan'
        discount = PlanDiscount.objects.filter(subplan=plan, total_months=months).first()
        discount_percent = Decimal(discount.total_discount) if discount else Decimal("0.00")

        subtotal = plan_price * months
        discounted_amount = subtotal - (subtotal * discount_percent / 100)
        total_amount += discounted_amount

    # --- Handle Cart Items ---
    for item in cart:
        product = item["product"]
        quantity = item["quantity"]
        price = Decimal(product.price)
        total_amount += price * quantity

    # --- Validate total ---
    if total_amount <= 0:
        messages.error(request, "Your total amount is invalid.")
        return redirect("checkout_preview")

    # --- Create Local Order ---
    order = Order.objects.create(
        user=request.user,
        plan=plan,
        total_amount=total_amount,
        status="paid",  # or "pending" if manual verification required
    )

    # Create order items for all products
    for item in cart:
        product = item["product"]
        quantity = item["quantity"]
        price = Decimal(product.price)
        OrderItem.objects.create(
            order=order,
            product=product,
            name=product.name,
            quantity=quantity,
            price=price,
            total_price=price * quantity,
        )

    # Create order item for subscription plan if selected
    if plan:
        OrderItem.objects.create(
            order=order,
            plan=plan,
            name=f"Subscription - {plan.title}",
            quantity=1,
            price=plan.price,
            total_price=plan.price,
        )
        plan.total_members += 1
        plan.save()

    # --- Clear cart + redirect to success ---
    cart.clear()
    messages.success(request, f"Order #{order.id} completed successfully! Total: £{total_amount:.2f}")

    return redirect(f"{reverse('checkout_success')}?order_id={order.id}")


@login_required
def checkout_success(request):
    """
    After successful checkout:
    - Show order summary
    - (Plan activation & cart clearing handled in checkout_session)
    """
    order_id = request.GET.get("order_id")
    order = Order.objects.filter(id=order_id, user=request.user).first()

    return render(request, 'checkout/success.html', {"order": order})


@login_required
def checkout_cancel(request):
    """Handles user cancellation of checkout."""
    return render(request, 'checkout/cancel.html')