from django.db import models
from django.contrib.auth.models import User


class SubPlan(models.Model):
    title = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_member = models.IntegerField(null=True)
    highlight_status = models.BooleanField(default=False, null=True)
    validity_days = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class SubPlanFeature(models.Model):
    subplan = models.ManyToManyField(SubPlan)
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title


class PlanDiscount(models.Model):
    subplan = models.ForeignKey(SubPlan, on_delete=models.CASCADE, null=True)
    total_months = models.IntegerField()
    total_discount = models.IntegerField()

    def __str__(self):
        return str(self.total_months)


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubPlan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.title}"
