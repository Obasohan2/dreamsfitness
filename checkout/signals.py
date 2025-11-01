from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from subscriptions.models import SubPlan


@receiver(post_save, sender=Order)
def update_plan_members_on_payment(sender, instance, created, **kwargs):
    """
    Automatically update SubPlan.total_members when an order is paid or cancelled.
    """
    plan = instance.plan
    if not plan:
        return

    # If a new paid order is created
    if created and instance.status == "paid":
        plan.total_members += 1
        plan.save()

    # If an existing order’s status changes to paid
    elif not created:
        # Get the previous version from the database
        previous = sender.objects.get(id=instance.id)
        if previous.status != instance.status:
            if instance.status == "paid":
                plan.total_members += 1
            elif instance.status in ["cancelled", "failed"] and plan.total_members > 0:
                plan.total_members -= 1
            plan.save()
