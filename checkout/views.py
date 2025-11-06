from django.shortcuts import render
from . import models


def checkout(request, plan_id):
    planDetail = models.SubPlan.objects.get(pk=plan_id)
    return render(request, 'checkout/checkout.html', {'plan': planDetail})
