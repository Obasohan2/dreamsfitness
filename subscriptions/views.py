from django.shortcuts import render, get_object_or_404, redirect
from itertools import chain
from django.contrib.auth.decorators import login_required
from .models import SubPlan, SubPlanFeature, DynamicFeature


def pricing_view(request):
    # Fetch all plans ordered by price
    plans = SubPlan.objects.prefetch_related('subplanfeature_set', 'dynamicfeature_set').order_by('price')

    # Combine SubPlanFeature and DynamicFeature, removing duplicates by title
    features = chain(
        SubPlanFeature.objects.prefetch_related('subplan').order_by('title'),
        DynamicFeature.objects.prefetch_related('subplan').order_by('title')
    )

    # Remove duplicate feature titles
    seen_titles = set()
    unique_features = []
    for f in features:
        if f.title not in seen_titles:
            unique_features.append(f)
            seen_titles.add(f.title)

    # Strictly reflect database — no auto-adding Elite Plan
    return render(request, 'subscriptions/pricing.html', {
        'plans': plans,
        'dfeatures': unique_features,
    })


@login_required
def checkout(request, plan_id):
    plan = get_object_or_404(
        SubPlan.objects.prefetch_related('subplanfeature_set', 'plandiscount_set'),
        pk=plan_id
    )

    total_members = getattr(plan, 'total_members', 0)
    balance_seats = (plan.max_member or 0) - total_members
    is_full = balance_seats <= 0

    return render(request, 'checkout/checkout.html', {
    'plan': plan,
    'balance_seats': balance_seats,
    'is_full': is_full,
})




@login_required
def checkout_session(request, plan_id):
    """
    Placeholder for checkout session (Stripe or PayPal integration later).
    For now, it just redirects back to checkout confirmation.
    """
    plan = get_object_or_404(SubPlan, pk=plan_id)

    # Example placeholder — later this can redirect to Stripe session
    return redirect('checkout', plan_id=plan.id)