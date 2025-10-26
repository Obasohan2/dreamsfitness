from django.db import models


class SubPlan(models.Model):  # Subscription plans
    title = models.CharField(max_length=150)
    price = models.IntegerField()
    max_member = models.IntegerField(null=True, blank=True)
    total_members = models.PositiveIntegerField(default=0)  # ✅ fixed indentation
    highlight_status = models.BooleanField(default=False, null=True)
    validity_days = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class PlanDiscount(models.Model):  # Discounts based on duration
    subplan = models.ForeignKey(SubPlan, on_delete=models.CASCADE, null=True)
    total_months = models.IntegerField()
    total_discount = models.IntegerField()

    def __str__(self):
        return f"{self.total_months} months - {self.total_discount}% off"


class SubPlanFeature(models.Model):  # Features for subscription plans
    subplan = models.ManyToManyField(SubPlan)
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title


class DynamicFeature(models.Model):  # Dynamic (add-on) features for plans
    title = models.CharField(max_length=100)
    subplan = models.ManyToManyField(SubPlan)

    def __str__(self):
        return self.title
