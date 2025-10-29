from django.contrib import admin
from .models import SubPlan, SubPlanFeature, PlanDiscount, DynamicFeature


@admin.register(SubPlan)
class SubPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'max_member', 'total_members', 'validity_days', 'highlight_status')
    list_editable = ('highlight_status', 'max_member')
    search_fields = ('title',)
    list_filter = ('highlight_status', 'validity_days')
    ordering = ('price',)
    readonly_fields = ('total_members',)  # Optional: protect member count from edits


@admin.register(SubPlanFeature)
class SubPlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_subplans')
    search_fields = ('title', 'subplan__title')
    list_filter = ('subplan',)

    def get_subplans(self, obj):
        """Display related subplans in a single line."""
        return " | ".join([sub.title for sub in obj.subplan.all()])
    get_subplans.short_description = 'Sub Plans'


@admin.register(PlanDiscount)
class PlanDiscountAdmin(admin.ModelAdmin):
    list_display = ('subplan', 'total_months', 'total_discount')
    list_filter = ('subplan',)
    search_fields = ('subplan__title',)


@admin.register(DynamicFeature)
class DynamicFeatureAdmin(admin.ModelAdmin):
    list_display = ('title',)
    filter_horizontal = ('subplan',)
