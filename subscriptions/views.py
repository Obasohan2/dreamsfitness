from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import SubPlan, SubPlanFeature


def pricing(request):
    plans = (
        SubPlan.objects
        .annotate(total_members=Count('subscriptions'))
        .order_by('price')
    )
    dfeatures = SubPlanFeature.objects.all()
    return render(request, 'subscriptions/pricing.html', {
        'plans': plans,
        'dfeatures': dfeatures
    })


def checkout(request, plan_id):
    planDetail = get_object_or_404(SubPlan, pk=plan_id)
    return render(request, 'checkout/checkout.html', {'plan': planDetail})
