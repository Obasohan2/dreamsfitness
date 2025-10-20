from django.shortcuts import render
from itertools import chain
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
