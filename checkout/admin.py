from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "quantity", "price", "total_price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "plan", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "plan__title")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Order Info", {
            "fields": ("user", "plan", "status", "total_amount")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    # Add the custom admin action
    actions = ["mark_as_paid", "mark_as_cancelled"]

    @admin.action(description="Mark selected orders as Paid")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="paid")
        self.message_user(request, f"{updated} order(s) marked as Paid.")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")
