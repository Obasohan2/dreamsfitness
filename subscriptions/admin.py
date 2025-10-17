from django.contrib import admin

# Register your models here.


from django.contrib import admin
from . import models


@admin.register(models.SubPlan)
class SubPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'max_member', 'validity_days', 'highlight_status')
    list_editable = ('highlight_status', 'max_member')


@admin.register(models.SubPlanFeature)
class SubPlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'subplans')

    def subplans(self, obj):
        return " | ".join(sub.title for sub in obj.subplan.all())
    subplans.short_description = 'Associated Plans'
