from django.db import models

# Create your models here.


# Subscription Plans
class SubPlan(models.Model):
	title = models.CharField(max_length=150)
	price = models.IntegerField()
	max_member = models.IntegerField(null=True)
	highlight_status = models.BooleanField(default=False,null=True)
	validity_days = models.IntegerField(null=True)

	def __str__(self):
		return self.title


# Subscription Plans Features
class SubPlanFeature(models.Model):
	subplan = models.ManyToManyField(SubPlan)
	title = models.CharField(max_length=150)

	def __str__(self):
		return self.title
