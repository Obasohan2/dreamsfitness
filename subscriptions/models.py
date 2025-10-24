from django.db import models

# Create your models here.


class SubPlan(models.Model):  # subscription plans
	title = models.CharField(max_length=150)
	price = models.IntegerField()
	max_member = models.IntegerField(null=True)
	highlight_status = models.BooleanField(default=False,null=True)
	validity_days = models.IntegerField(null=True)

	def __str__(self):
		return self.title


class PlanDiscount(models.Model):
    subplan = models.ForeignKey(SubPlan, on_delete=models.CASCADE, null=True)
    total_months = models.IntegerField()
    total_discount = models.IntegerField()

    def __str__(self):
        return str(self.total_months)


class SubPlanFeature(models.Model):  # features for subscription plans
	subplan = models.ManyToManyField(SubPlan)
	title = models.CharField(max_length=150)

	def __str__(self):
		return self.title


class DynamicFeature(models.Model):   # dynamic features for subscription plans
    title = models.CharField(max_length=100)
    subplan = models.ManyToManyField(SubPlan)
    
    def __str__(self):
        return self.title